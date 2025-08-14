"""
Experiment Execution Module
===========================

Handles execution of baseline and mitigation experiments.
"""

import os
import sys
import time
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List
import numpy as np

from config.study_config import StudyConfiguration, BASELINE_CONFIGURATIONS
from utils.helpers import (
    set_random_seeds, check_mitigation_dependencies, 
    parse_test_result, calculate_flakiness_index,
    create_mock_conftest_content, validate_output_directory
)


class BaselineRunner:
    """Executes baseline experiments to establish flakiness patterns"""
    
    def __init__(self, config: StudyConfiguration):
        self.config = config
        self.output_dir = validate_output_directory(Path(config.output_dir))
    
    def run_experiments(self) -> Dict:
        """Execute baseline experiments for all flakiness types"""
        if self.config.skip_baseline:
            print("⏭️  Skipping baseline experiments")
            return {}
        
        print("🔬 PHASE 1: BASELINE ANALYSIS")
        print("=" * 50)
        print("Executing tests without mitigation to establish flakiness patterns")
        print(f"Runs per configuration: {self.config.baseline_runs}")
        print(f"Seeds: {self.config.seeds}")
        print()
        
        baseline_data = {}
        
        for config in BASELINE_CONFIGURATIONS:
            print(f"🧪 Testing: {config['name']} - {config['description']}")
            
            config_results = []
            config_start = time.time()
            
            for seed in self.config.seeds:
                if self.config.verbose:
                    print(f"   🌱 Seed: {seed}")
                
                for run in range(1, self.config.baseline_runs + 1):
                    result = self._execute_test_run(
                        markers=config['markers'],
                        run_number=run,
                        seed=seed,
                        output_file=self.output_dir / f"baseline_{config['name']}_seed_{seed}_run_{run:03d}.json"
                    )
                    config_results.append(result)
                    
                    if not self.config.verbose and run % 10 == 0:
                        avg_pass_rate = np.mean([r['pass_rate'] for r in config_results if r['pass_rate'] is not None])
                        print(f"   Progress: seed {seed}, run {run}/{self.config.baseline_runs} (avg pass rate: {avg_pass_rate:.1%})")
            
            config_duration = time.time() - config_start
            
            # Calculate statistics
            valid_results = [r for r in config_results if r['pass_rate'] is not None]
            
            baseline_data[config['name']] = {
                'configuration': config,
                'results': config_results,
                'duration': config_duration,
                'total_runs': len(config_results),
                'valid_runs': len(valid_results),
                'avg_pass_rate': np.mean([r['pass_rate'] for r in valid_results]) if valid_results else 0,
                'std_pass_rate': np.std([r['pass_rate'] for r in valid_results]) if valid_results else 0,
                'flakiness_index': calculate_flakiness_index(valid_results),
            }
            
            print(f"   ✅ Completed in {config_duration:.1f}s (avg pass rate: {baseline_data[config['name']]['avg_pass_rate']:.1%})")
            print()
        
        return baseline_data
    
    def _execute_test_run(self, markers: str, run_number: int, seed: int, output_file: Path) -> Dict:
        """Execute a single baseline test run"""
        # Set seed for this run
        if markers == "randomness":
            # For randomness tests, use run-specific seed to preserve flakiness
            run_seed = (seed * 1000) + run_number
            set_random_seeds(run_seed)
        else:
            set_random_seeds(seed)
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-m", markers,
            "--json-report",
            f"--json-report-file={output_file}",
            "-q"
        ]
        
        env = os.environ.copy()
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        execution_time = time.time() - start_time
        
        return parse_test_result(output_file, run_number, execution_time, 
                               result.returncode, markers, seed)


class MitigationRunner:
    """Executes mitigation strategy experiments"""
    
    def __init__(self, config: StudyConfiguration):
        self.config = config
        self.output_dir = validate_output_directory(Path(config.output_dir))
    
    def run_experiments(self) -> Dict:
        """Execute mitigation strategy experiments"""
        if self.config.skip_mitigation:
            print("⏭️  Skipping mitigation experiments")
            return {}
        
        print("🛠️  PHASE 2: MITIGATION ANALYSIS")
        print("=" * 50)
        print("Testing 4 mitigation strategies against flaky tests")
        print()
        
        # Check dependencies
        if not check_mitigation_dependencies():
            print("❌ Missing required dependencies for mitigation tests")
            return {}
        
        strategies = {
            'retries': self._run_retry_strategy,
            'mocking': self._run_mocking_strategy,
            'isolation': self._run_isolation_strategy,
            'combined': self._run_combined_strategy
        }
        
        mitigation_data = {}
        
        for strategy_name, strategy_func in strategies.items():
            print(f"🔧 Testing strategy: {strategy_name.upper()}")
            
            strategy_start = time.time()
            strategy_results = []
            
            for run in range(1, self.config.mitigation_runs + 1):
                result = strategy_func(run)
                strategy_results.append(result)
                
                if not self.config.verbose and run % 5 == 0:
                    avg_pass_rate = np.mean([r['pass_rate'] for r in strategy_results if r['pass_rate'] is not None])
                    print(f"   Progress: run {run}/{self.config.mitigation_runs} (avg pass rate: {avg_pass_rate:.1%})")
            
            strategy_duration = time.time() - strategy_start
            
            # Calculate statistics
            valid_results = [r for r in strategy_results if r['pass_rate'] is not None]
            
            mitigation_data[strategy_name] = {
                'strategy': strategy_name,
                'results': strategy_results,
                'duration': strategy_duration,
                'total_runs': len(strategy_results),
                'valid_runs': len(valid_results),
                'avg_pass_rate': np.mean([r['pass_rate'] for r in valid_results]) if valid_results else 0,
                'std_pass_rate': np.std([r['pass_rate'] for r in valid_results]) if valid_results else 0,
                'avg_execution_time': np.mean([r['execution_time'] for r in valid_results]) if valid_results else 0,
            }
            
            print(f"   ✅ Completed in {strategy_duration:.1f}s (avg pass rate: {mitigation_data[strategy_name]['avg_pass_rate']:.1%})")
            print()
        
        return mitigation_data
    
    def _run_retry_strategy(self, run_number: int) -> Dict:
        """Execute retry mitigation strategy"""
        output_file = self.output_dir / f"mitigation_retries_run_{run_number:03d}.json"
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-m", "flaky",
            "--reruns=3",
            "--reruns-delay=1",
            "--json-report",
            f"--json-report-file={output_file}",
            "-q"
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        execution_time = time.time() - start_time
        
        return parse_test_result(output_file, run_number, execution_time, result.returncode)
    
    
    def _run_mocking_strategy(self, run_number: int) -> Dict:
        """Execute mocking mitigation strategy"""
        output_file = self.output_dir / f"mitigation_mocking_run_{run_number:03d}.json"
        
        # Create temporary conftest with mocks
        conftest_content = create_mock_conftest_content()
        conftest_path = Path("tests/conftest.py")
        
        try:
            with open(conftest_path, 'w') as f:
                f.write(conftest_content)
            
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/",
                "-m", "flaky",
                "--json-report",
                f"--json-report-file={output_file}",
                "-q"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            execution_time = time.time() - start_time
            
            return parse_test_result(output_file, run_number, execution_time, result.returncode)
            
        finally:
            if conftest_path.exists():
                conftest_path.unlink()
    
    def _run_isolation_strategy(self, run_number: int) -> Dict:
        """Execute isolation mitigation strategy"""
        output_file = self.output_dir / f"mitigation_isolation_run_{run_number:03d}.json"
        
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-m", "flaky",
            "--forked",
            "--json-report",
            f"--json-report-file={output_file}",
            "-q"
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        execution_time = time.time() - start_time
        
        return parse_test_result(output_file, run_number, execution_time, result.returncode)
    
    def _run_combined_strategy(self, run_number: int) -> Dict:
        """Execute combined mitigation strategy"""
        output_file = self.output_dir / f"mitigation_combined_run_{run_number:03d}.json"
        
        # Create temporary conftest with mocks
        conftest_content = create_mock_conftest_content()
        conftest_path = Path("tests/conftest.py")
        
        try:
            with open(conftest_path, 'w') as f:
                f.write(conftest_content)
            
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/",
                "-m", "flaky",
                "--reruns=2",
                "--reruns-delay=0.5",
                "--forked",
                "--json-report",
                f"--json-report-file={output_file}",
                "-q"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            execution_time = time.time() - start_time
            
            return parse_test_result(output_file, run_number, execution_time, result.returncode)
            
        finally:
            if conftest_path.exists():
                conftest_path.unlink()
