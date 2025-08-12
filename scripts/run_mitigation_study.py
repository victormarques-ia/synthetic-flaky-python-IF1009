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
import tempfile
import shutil


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
    
    def run_baseline(self):
        """Executes baseline without mitigation - only stable tests"""
        print("🔬 Running BASELINE (no mitigation)...")
        
        all_results = []
        total_passed = 0
        total_tests = 0
        
        for seed in self.seeds:
            print(f"   🌱 Using seed: {seed}")
            self.set_random_seeds(seed)
            
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/",
                "-m", "stable",  # Run only stable tests for true baseline
                "--json-report",
                f"--json-report-file={self.output_dir}/baseline_seed_{seed}.json",
                "-v"
            ]
            
            env = os.environ.copy()
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            duration = time.time() - start_time
            
            # Parse JSON results to get actual pass/fail counts
            json_file = self.output_dir / f"baseline_seed_{seed}.json"
            if json_file.exists():
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                    summary = json_data.get('summary', {})
                    passed = summary.get('passed', 0)
                    total = summary.get('total', 0)  # Use 'total' (actually run) not 'collected' (including deselected)
                    total_passed += passed
                    total_tests += total
            
            all_results.append({
                'seed': seed,
                'success': result.returncode == 0,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            })
        
        # Calculate real success rate based on test results, not process exit codes
        avg_duration = sum(r['duration'] for r in all_results) / len(all_results)
        success_rate = total_passed / max(total_tests, 1)  # Use actual test pass rate
        
        self.results['baseline'] = {
            'success': success_rate > 0.5,
            'duration': avg_duration,
            'all_results': all_results,
            'success_rate': success_rate,
            'total_passed': total_passed,
            'total_tests': total_tests
        }
        
        print(f"   ✅ Completed in {avg_duration:.1f}s avg (success rate: {success_rate:.1%})")
        return success_rate > 0.5
    
    def run_retries(self):
        """Executes with retry strategy"""
        print("🔄 Running RETRIES...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "--reruns=3",
            "--reruns-delay=1",
            "--json-report", 
            f"--json-report-file={self.output_dir}/retries.json",
            "-v"
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        self.results['retries'] = {
            'success': result.returncode == 0,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
        print(f"   ✅ Completed in {duration:.1f}s")
        return result.returncode == 0
    
    def create_mock_conftest(self):
        """Creates temporary conftest.py with mocks"""
        conftest_content = '''"""
Temporary configuration for tests with mocking
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def mock_external_dependencies():
    """Mock unstable external dependencies"""
    
    # Mock external API to always return success
    with patch('tests.test_flaky_external.MockExternalAPI.get_user_data') as mock_api:
        mock_api.return_value = {"id": 123, "name": "MockUser", "active": True}
        
        # Mock Database to always connect
        with patch('tests.test_flaky_external.MockDatabase.connect') as mock_db_connect:
            mock_db_connect.return_value = True
            
            # Mock Database query to always return data
            with patch('tests.test_flaky_external.MockDatabase.query') as mock_db_query:
                mock_db_query.return_value = [{"id": 1, "data": "mocked"}]
                
                yield
'''
        
        conftest_path = Path("tests/conftest.py")
        with open(conftest_path, 'w') as f:
            f.write(conftest_content)
        
        return conftest_path
    
    def run_mocking(self):
        """Executes with mocking strategy"""
        print("🎭 Running MOCKING...")
        
        # Create temporary conftest
        conftest_path = self.create_mock_conftest()
        
        try:
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/",
                "--json-report",
                f"--json-report-file={self.output_dir}/mocking.json",
                "-v"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = time.time() - start_time
            
            self.results['mocking'] = {
                'success': result.returncode == 0,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            print(f"   ✅ Completed in {duration:.1f}s")
            return result.returncode == 0
            
        finally:
            # Remove temporary conftest
            if conftest_path.exists():
                conftest_path.unlink()
    
    def run_isolation(self):
        """Executes with isolation strategy"""
        print("🧹 Running ISOLATION...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "--forked",  # Execute each test in separate process
            "--json-report",
            f"--json-report-file={self.output_dir}/isolation.json",
            "-v"
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        self.results['isolation'] = {
            'success': result.returncode == 0,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
        print(f"   ✅ Completed in {duration:.1f}s")
        return result.returncode == 0
    
    def run_combined(self):
        """Executes with all strategies combined"""
        print("🚀 Running COMBINED (retries + mocking + isolation)...")
        
        # Create temporary conftest for mocking
        conftest_path = self.create_mock_conftest()
        
        try:
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/",
                "--reruns=2",  # Fewer retries to avoid being too slow
                "--reruns-delay=0.5",
                "--forked",
                "--json-report",
                f"--json-report-file={self.output_dir}/combined.json",
                "-v"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = time.time() - start_time
            
            self.results['combined'] = {
                'success': result.returncode == 0,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            print(f"   ✅ Completed in {duration:.1f}s")
            return result.returncode == 0
            
        finally:
            # Remove temporary conftest
            if conftest_path.exists():
                conftest_path.unlink()
    
    def analyze_results(self):
        """Analyzes and compares all results"""
        print("\n📊 Analyzing results...")
        
        analysis = {}
        
        for strategy in ['baseline', 'retries', 'mocking', 'isolation', 'combined']:
            if strategy == 'baseline':
                # Special handling for baseline with multiple seed files
                total_collected = 0
                total_passed = 0
                total_failed = 0
                total_skipped = 0
                
                for seed in self.seeds:
                    result_file = self.output_dir / f"baseline_seed_{seed}.json"
                    if result_file.exists():
                        with open(result_file, 'r') as f:
                            data = json.load(f)
                        
                        summary = data.get('summary', {})
                        total_collected += summary.get('total', 0)  # Use 'total' for consistency
                        total_passed += summary.get('passed', 0)
                        total_failed += summary.get('failed', 0)
                        total_skipped += summary.get('skipped', 0)
                
                analysis[strategy] = {
                    'tests_collected': total_collected,
                    'tests_passed': total_passed,
                    'tests_failed': total_failed,
                    'tests_skipped': total_skipped,
                    'pass_rate': total_passed / max(total_collected, 1),
                    'duration': self.results.get(strategy, {}).get('duration', 0)
                }
            else:
                # Standard handling for other strategies
                result_file = self.output_dir / f"{strategy}.json"
                
                if result_file.exists():
                    with open(result_file, 'r') as f:
                        data = json.load(f)
                    
                    summary = data.get('summary', {})
                    
                    analysis[strategy] = {
                        'tests_collected': summary.get('collected', 0),
                        'tests_passed': summary.get('passed', 0),
                        'tests_failed': summary.get('failed', 0),
                        'tests_skipped': summary.get('skipped', 0),
                        'pass_rate': summary.get('passed', 0) / max(summary.get('collected', 1), 1),
                        'duration': self.results.get(strategy, {}).get('duration', 0)
                    }
        
        return analysis
    
    def print_comparison_report(self, analysis):
        """Prints comparative report"""
        print("\n" + "="*70)
        print("📋 MITIGATION STUDY RESULTS")
        print("="*70)
        
        # Get baseline for comparison
        baseline = analysis.get('baseline', {})
        baseline_passed = baseline.get('tests_passed', 0)
        baseline_rate = baseline.get('pass_rate', 0)
        baseline_time = baseline.get('duration', 0)
        
        strategies = ['baseline', 'retries', 'mocking', 'isolation', 'combined']
        
        for strategy in strategies:
            if strategy not in analysis:
                continue
                
            data = analysis[strategy]
            
            print(f"\n🔬 {strategy.upper()}:")
            print(f"   Tests passed: {data['tests_passed']}/{data['tests_collected']}")
            print(f"   Success rate: {data['pass_rate']:.1%}")
            print(f"   Execution time: {data['duration']:.1f}s")
            
            if strategy != 'baseline':
                # Calculate improvements
                tests_saved = data['tests_passed'] - baseline_passed
                rate_improvement = (data['pass_rate'] - baseline_rate) * 100
                time_overhead = ((data['duration'] - baseline_time) / baseline_time * 100) if baseline_time > 0 else 0
                
                print(f"   📈 Tests saved: {tests_saved:+d}")
                print(f"   📈 Rate improvement: {rate_improvement:+.1f}%")
                print(f"   ⏱️ Time overhead: {time_overhead:+.1f}%")
        
        # Effectiveness ranking
        print(f"\n🏆 EFFECTIVENESS RANKING:")
        effectiveness_ranking = []
        
        for strategy in ['retries', 'mocking', 'isolation', 'combined']:
            if strategy in analysis:
                data = analysis[strategy]
                tests_saved = data['tests_passed'] - baseline_passed
                rate_improvement = (data['pass_rate'] - baseline_rate) * 100
                time_overhead = ((data['duration'] - baseline_time) / baseline_time * 100) if baseline_time > 0 else 0
                
                # Simple score: improvement - overhead/10 (to penalize high overhead)
                effectiveness_score = rate_improvement - (time_overhead / 10)
                
                effectiveness_ranking.append({
                    'strategy': strategy,
                    'score': effectiveness_score,
                    'tests_saved': tests_saved,
                    'rate_improvement': rate_improvement,
                    'time_overhead': time_overhead
                })
        
        # Sort by score
        effectiveness_ranking.sort(key=lambda x: x['score'], reverse=True)
        
        for i, item in enumerate(effectiveness_ranking, 1):
            print(f"   {i}. {item['strategy'].upper()}: "
                  f"score {item['score']:.1f} "
                  f"({item['tests_saved']:+d} tests, {item['rate_improvement']:+.1f}%, {item['time_overhead']:+.1f}% time)")
    
    def save_study_data(self, analysis):
        """Saves study data for later analysis"""
        study_data = {
            'experiment_info': {
                'timestamp': datetime.now().isoformat(),
                'study_type': 'mitigation_comparison',
                'strategies_tested': list(analysis.keys())
            },
            'results': analysis,
            'execution_details': self.results
        }
        
        output_file = self.output_dir / "mitigation_study_results.json"
        with open(output_file, 'w') as f:
            json.dump(study_data, f, indent=2)
        
        return output_file


def check_dependencies():
    """Checks if required dependencies are installed"""
    required_packages = ['pytest-rerunfailures', 'pytest-forked']
    missing = []
    
    for package in required_packages:
        try:
            subprocess.run([sys.executable, "-c", f"import {package.replace('-', '_')}"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print(f"📦 Install with: pip install {' '.join(missing)}")
        return False
    
    return True


def main():
    """Executes complete mitigation study"""
    print("🧪 EMPIRICAL STUDY: Flaky Test Mitigation Techniques")
    print("Comparing baseline vs 4 mitigation strategies")
    print()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Execute experiments with seeds for robustness
    seeds = [42, 123, 999]  # Fixed seeds for reproducibility
    experiment = MitigationExperiment(seeds=seeds)
    
    print(f"🌱 Using seeds: {seeds} for robustness")
    print()
    
    try:
        # Execute all strategies
        experiment.run_baseline()
        experiment.run_retries()
        experiment.run_mocking()
        experiment.run_isolation() 
        experiment.run_combined()
        
        # Analyze results
        analysis = experiment.analyze_results()
        
        # Generate report
        experiment.print_comparison_report(analysis)
        
        # Save data
        output_file = experiment.save_study_data(analysis)
        
        print(f"\n📁 Complete data saved in: {output_file}")
        
    except KeyboardInterrupt:
        print("\n❌ Experiment interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during experiment: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
