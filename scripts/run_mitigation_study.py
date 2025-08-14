#!/usr/bin/env python3
"""
Empirical Study of Flaky Test Mitigation Techniques
Executes baseline + 4 mitigation strategies and compares results.
"""

import subprocess
import json
import sys
import time
import os
import random
import numpy as np
from pathlib import Path
from datetime import datetime

class MitigationExperiment:
    """Class to execute mitigation experiments"""
    
    def __init__(self, output_dir="mitigation_results", seeds=[42, 123, 999]):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {}
        self.seeds = seeds
        
    def set_random_seeds(self, seed):
        """Set random seeds for reproducibility"""
        random.seed(seed)
        np.random.seed(seed)
        os.environ['PYTHONHASHSEED'] = str(seed)
        os.environ['RANDOM_SEED'] = str(seed)

    def _execute_strategy(self, strategy_name, pytest_cmd):
        """Helper function to run a strategy for all seeds"""
        print(f"🔬 Running {strategy_name.upper()}...")
        
        all_run_details = []
        total_duration = 0

        for seed in self.seeds:
            print(f"    🌱 Using seed: {seed}")
            self.set_random_seeds(seed)
            
            final_cmd = list(pytest_cmd) # Make a copy
            
            # --- CORREÇÃO APLICADA AQUI ---
            # Em vez de procurar e substituir, simplesmente adicionamos o argumento do arquivo de saída.
            output_file_arg = f"--json-report-file={self.output_dir}/{strategy_name}_seed_{seed}.json"
            final_cmd.append(output_file_arg)
            # --- FIM DA CORREÇÃO ---

            env = os.environ.copy()
            start_time = time.time()
            result = subprocess.run(final_cmd, capture_output=True, text=True, env=env)
            duration = time.time() - start_time
            total_duration += duration

            all_run_details.append({
                'seed': seed,
                'success': result.returncode == 0,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            })

        avg_duration = total_duration / len(self.seeds) if self.seeds else 0
        self.results[strategy_name] = {
            'duration': avg_duration,
            'all_results': all_run_details,
        }
        print(f"    ✅ Completed in {avg_duration:.1f}s avg")
        return True

    def run_baseline(self):
        cmd = [sys.executable, "-m", "pytest", "tests/", "--json-report", "-v"]
        return self._execute_strategy('baseline', cmd)
        
    def run_retries(self):
        cmd = [sys.executable, "-m", "pytest", "tests/", "--reruns=3", "--reruns-delay=1", "--json-report", "-v"]
        return self._execute_strategy('retries', cmd)

    def create_mock_conftest(self):
        conftest_content = '''"""Temporary conftest for mocking"""
import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_external_dependencies():
    with patch('tests.test_flaky_external.MockExternalAPI.get_user_data') as mock_api, \
         patch('tests.test_flaky_external.MockDatabase.connect') as mock_db_connect, \
         patch('tests.test_flaky_external.MockDatabase.query') as mock_db_query:
        mock_api.return_value = {"id": 123, "name": "MockUser", "active": True}
        mock_db_connect.return_value = True
        mock_db_query.return_value = [{"id": 1, "data": "mocked"}]
        yield
'''
        conftest_path = Path("tests/conftest.py")
        with open(conftest_path, 'w') as f:
            f.write(conftest_content)
        return conftest_path

    def run_mocking(self):
        conftest_path = self.create_mock_conftest()
        try:
            cmd = [sys.executable, "-m", "pytest", "tests/", "--json-report", "-v"]
            return self._execute_strategy('mocking', cmd)
        finally:
            if conftest_path.exists():
                conftest_path.unlink()
    
    def run_isolation(self):
        cmd = [sys.executable, "-m", "pytest", "tests/", "--forked", "--json-report", "-v"]
        return self._execute_strategy('isolation', cmd)
        
    def run_combined(self):
        conftest_path = self.create_mock_conftest()
        try:
            cmd = [sys.executable, "-m", "pytest", "tests/", "--reruns=2", "--reruns-delay=0.5", "--forked", "--json-report", "-v"]
            return self._execute_strategy('combined', cmd)
        finally:
            if conftest_path.exists():
                conftest_path.unlink()

    def analyze_results(self):
        """Analyzes and compares all results by aggregating data from all seeds."""
        print("\n📊 Analyzing results...")
        analysis = {}
        
        strategies = ['baseline', 'retries', 'mocking', 'isolation', 'combined']
        for strategy in strategies:
            if strategy not in self.results:
                continue

            total_collected, total_passed, total_failed, total_skipped = 0, 0, 0, 0
            
            for seed in self.seeds:
                result_file = self.output_dir / f"{strategy}_seed_{seed}.json"
                if result_file.exists():
                    with open(result_file, 'r') as f:
                        data = json.load(f)
                    summary = data.get('summary', {})
                    total_collected += summary.get('total', 0)
                    total_passed += summary.get('passed', 0)
                    total_failed += summary.get('failed', 0)
                    total_skipped += summary.get('skipped', 0)
            
            analysis[strategy] = {
                'tests_collected': total_collected,
                'tests_passed': total_passed,
                'tests_failed': total_failed,
                'tests_skipped': total_skipped,
                'pass_rate': total_passed / max(total_collected, 1),
                'duration': self.results[strategy].get('duration', 0)
            }
        return analysis

    def print_comparison_report(self, analysis):
        """Prints comparative report"""
        print("\n" + "="*70)
        print("📋 MITIGATION STUDY RESULTS")
        print("="*70)
        
        baseline = analysis.get('baseline', {})
        baseline_rate = baseline.get('pass_rate', 0)
        baseline_time = baseline.get('duration', 0)
        
        for strategy in ['baseline', 'retries', 'mocking', 'isolation', 'combined']:
            if strategy not in analysis: continue
            
            data = analysis[strategy]
            print(f"\n🔬 {strategy.upper()}:")
            print(f"    Tests passed: {data['tests_passed']}/{data['tests_collected']}")
            print(f"    Success rate: {data['pass_rate']:.1%}")
            print(f"    Execution time: {data['duration']:.1f}s")
            
            if strategy != 'baseline':
                rate_improvement = (data['pass_rate'] - baseline_rate) * 100
                time_overhead = ((data['duration'] - baseline_time) / baseline_time * 100) if baseline_time > 0 else 0
                print(f"    📈 Rate improvement: {rate_improvement:+.1f}%")
                print(f"    ⏱️ Time overhead: {time_overhead:+.1f}%")

        print(f"\n🏆 EFFECTIVENESS RANKING (Rate Improvement vs. Time Overhead):")
        effectiveness_ranking = []
        for strategy in ['retries', 'mocking', 'isolation', 'combined']:
            if strategy in analysis:
                data = analysis[strategy]
                rate_improvement = (data['pass_rate'] - baseline_rate) * 100
                time_overhead = ((data['duration'] - baseline_time) / baseline_time * 100) if baseline_time > 0 else 0
                effectiveness_score = rate_improvement - (time_overhead / 10) # Simple score
                effectiveness_ranking.append({
                    'strategy': strategy, 'score': effectiveness_score,
                    'rate_improvement': rate_improvement, 'time_overhead': time_overhead
                })
        
        effectiveness_ranking.sort(key=lambda x: x['score'], reverse=True)
        
        for i, item in enumerate(effectiveness_ranking, 1):
            print(f"    {i}. {item['strategy'].upper()}: "
                  f"score {item['score']:.1f} "
                  f"({item['rate_improvement']:+.1f}% rate, {item['time_overhead']:+.1f}% time)")

def check_dependencies():
    """Checks if required dependencies are installed"""
    required_packages = ['pytest-rerunfailures', 'pytest-forked']
    missing = [pkg for pkg in required_packages if subprocess.run([sys.executable, "-c", f"import {pkg.replace('-', '_')}"], check=False, capture_output=True).returncode != 0]
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print(f"📦 Install with: pip install {' '.join(missing)}")
        return False
    return True

def main():
    """Executes complete mitigation study"""
    print("🧪 EMPIRICAL STUDY: Flaky Test Mitigation Techniques")
    if not check_dependencies(): return 1
    
    experiment = MitigationExperiment(seeds=[42, 123, 999])
    print(f"🌱 Using seeds: {experiment.seeds} for robustness\n")
    
    try:
        experiment.run_baseline()
        experiment.run_retries()
        experiment.run_mocking()
        experiment.run_isolation()
        experiment.run_combined()
        
        analysis = experiment.analyze_results()
        experiment.print_comparison_report(analysis)
        
    except Exception as e:
        print(f"\n❌ Error during experiment: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
