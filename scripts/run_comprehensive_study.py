#!/usr/bin/env python3
"""
Comprehensive Flaky Test Study
===============================

Unified script that executes complete empirical study of flaky test mitigation techniques.

Study Components:
1. Baseline Analysis - Execute tests without mitigation to establish flakiness patterns
2. Mitigation Analysis - Test 4 different mitigation strategies
3. Classification - Systematic analysis of 5 flakiness types
4. Effectiveness Metrics - Quantitative evaluation of each technique
5. Cost-Benefit Analysis - Performance overhead vs effectiveness
6. Practical Recommendations - Guidelines for developers

Authors: Synthetic Flaky Python Framework
"""

import subprocess
import json
import sys
import time
import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import argparse
import tempfile
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)


@dataclass
class StudyConfiguration:
    """Configuration for the comprehensive study"""
    baseline_runs: int = 30
    mitigation_runs: int = 10
    seeds: List[int] = None
    output_dir: str = "comprehensive_results"
    verbose: bool = False
    skip_baseline: bool = False
    skip_mitigation: bool = False
    
    def __post_init__(self):
        if self.seeds is None:
            self.seeds = [42, 123, 999]


@dataclass
class FlakynessProfile:
    """Profile of flakiness characteristics for a test type"""
    test_type: str
    description: str
    failure_mechanism: str
    typical_pass_rate: float
    mitigation_effectiveness: Dict[str, float]


class FlakynessClassifier:
    """Classifier for the 5 main types of flakiness"""
    
    @staticmethod
    def get_flakiness_profiles() -> Dict[str, FlakynessProfile]:
        """Define the 5 main flakiness types and their characteristics"""
        return {
            "randomness": FlakynessProfile(
                test_type="randomness",
                description="Tests dependent on random values or probabilistic outcomes",
                failure_mechanism="Non-deterministic assertions based on random values",
                typical_pass_rate=0.5,  # Highly variable
                mitigation_effectiveness={
                    "retries": 0.3,      # Some improvement through multiple attempts
                    "mocking": 0.9,      # High - can mock random functions
                    "isolation": 0.1,    # Low - doesn't address root cause
                    "combined": 0.9      # High - mocking is key
                }
            ),
            "timeout": FlakynessProfile(
                test_type="timeout",
                description="Tests sensitive to timing and performance variations",
                failure_mechanism="Time-dependent assertions failing under load or slow systems",
                typical_pass_rate=0.7,  # Often passes but fails under stress
                mitigation_effectiveness={
                    "retries": 0.6,      # Moderate - second attempt may succeed
                    "mocking": 0.4,      # Low-Moderate - can mock slow operations
                    "isolation": 0.8,    # High - reduces resource contention
                    "combined": 0.8      # High - isolation + retries work well
                }
            ),
            "order": FlakynessProfile(
                test_type="order",
                description="Tests dependent on execution order or global state",
                failure_mechanism="Shared state between tests causing order dependencies",
                typical_pass_rate=0.6,  # Depends on execution order
                mitigation_effectiveness={
                    "retries": 0.2,      # Low - same order issues persist
                    "mocking": 0.5,      # Moderate - can mock shared resources
                    "isolation": 0.9,    # High - prevents state sharing
                    "combined": 0.9      # High - isolation is key
                }
            ),
            "external": FlakynessProfile(
                test_type="external",
                description="Tests dependent on external systems (APIs, databases, network)",
                failure_mechanism="Network failures, service unavailability, or slow responses",
                typical_pass_rate=0.7,  # Often works but external failures occur
                mitigation_effectiveness={
                    "retries": 0.7,      # High - external issues often temporary
                    "mocking": 0.95,     # Very High - eliminates external dependency
                    "isolation": 0.3,    # Low - doesn't address external issues
                    "combined": 0.95     # Very High - mocking is key
                }
            ),
            "race": FlakynessProfile(
                test_type="race",
                description="Tests with race conditions and concurrency issues",
                failure_mechanism="Thread synchronization issues and timing-dependent failures",
                typical_pass_rate=0.8,  # Usually passes but occasionally fails
                mitigation_effectiveness={
                    "retries": 0.4,      # Moderate - may succeed on retry
                    "mocking": 0.6,      # Moderate - can mock concurrent operations
                                    "isolation": 0.9,    # High - eliminates concurrency issues
                    "combined": 0.9      # High - isolation prevents race conditions
                }
            )
        }


class ComprehensiveStudy:
    """Main class for executing the comprehensive flaky test study"""
    
    def __init__(self, config: StudyConfiguration):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize results storage
        self.baseline_results = {}
        self.mitigation_results = {}
        self.analysis_results = {}
        
        # Initialize classifier
        self.classifier = FlakynessClassifier()
        self.flakiness_profiles = self.classifier.get_flakiness_profiles()
        
        # Study metadata
        self.study_start_time = time.time()
        self.study_metadata = {
            "study_type": "comprehensive_flaky_test_analysis",
            "framework": "synthetic_flaky_python",
            "timestamp": datetime.now().isoformat(),
            "configuration": config.__dict__
        }
    
    def set_random_seeds(self, seed: int):
        """Set random seeds for reproducibility"""
        random.seed(seed)
        np.random.seed(seed)
        os.environ['PYTHONHASHSEED'] = str(seed)
        os.environ['RANDOM_SEED'] = str(seed)
    
    def run_baseline_experiments(self) -> Dict:
        """Execute baseline experiments to establish flakiness patterns"""
        if self.config.skip_baseline:
            print("⏭️  Skipping baseline experiments")
            return {}
        
        print("🔬 PHASE 1: BASELINE ANALYSIS")
        print("=" * 50)
        print("Executing tests without mitigation to establish flakiness patterns")
        print(f"Runs per configuration: {self.config.baseline_runs}")
        print(f"Seeds: {self.config.seeds}")
        print()
        
        # Test configurations with different flakiness levels
        configurations = [
            {"name": "stable_only", "markers": "stable", "description": "Stable tests only (0% flaky)"},
            {"name": "randomness", "markers": "randomness", "description": "Randomness-based flaky tests"},
            {"name": "timeout", "markers": "timeout", "description": "Timeout-based flaky tests"},
            {"name": "order", "markers": "order", "description": "Order-dependent flaky tests"},
            {"name": "external", "markers": "external", "description": "External dependency flaky tests"},
            {"name": "race", "markers": "race", "description": "Race condition flaky tests"},
            {"name": "all_flaky", "markers": "flaky", "description": "All flaky tests combined"},
        ]
        
        baseline_data = {}
        
        for config in configurations:
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
                'flakiness_index': self._calculate_flakiness_index(valid_results),
            }
            
            print(f"   ✅ Completed in {config_duration:.1f}s (avg pass rate: {baseline_data[config['name']]['avg_pass_rate']:.1%})")
            print()
        
        self.baseline_results = baseline_data
        return baseline_data
    
    def run_mitigation_experiments(self) -> Dict:
        """Execute mitigation strategy experiments"""
        if self.config.skip_mitigation:
            print("⏭️  Skipping mitigation experiments")
            return {}
        
        print("🛠️  PHASE 2: MITIGATION ANALYSIS")
        print("=" * 50)
        print("Testing 4 mitigation strategies against flaky tests")
        print()
        
        # Check dependencies
        if not self._check_mitigation_dependencies():
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
        
        self.mitigation_results = mitigation_data
        return mitigation_data
    
    def analyze_results(self) -> Dict:
        """Comprehensive analysis of all results"""
        print("📊 PHASE 3: COMPREHENSIVE ANALYSIS")
        print("=" * 50)
        print("Analyzing effectiveness, cost-benefit, and generating recommendations")
        print()
        
        analysis = {
            'flakiness_classification': self._analyze_flakiness_types(),
            'mitigation_effectiveness': self._analyze_mitigation_effectiveness(),
            'cost_benefit_analysis': self._analyze_cost_benefit(),
            'statistical_significance': self._analyze_statistical_significance(),
            'recommendations': self._generate_recommendations()
        }
        
        self.analysis_results = analysis
        return analysis
    
    def generate_report(self):
        """Generate comprehensive final report"""
        print("📋 PHASE 4: REPORT GENERATION")
        print("=" * 50)
        
        # Generate visualizations
        self._create_visualizations()
        
        # Generate text report
        report_content = self._generate_text_report()
        
        # Save all data
        self._save_all_data()
        
        # Print final summary
        self._print_final_summary()
    
    def _execute_test_run(self, markers: str, run_number: int, seed: int, output_file: Path) -> Dict:
        """Execute a single test run"""
        # Set seed for this run
        if markers == "randomness":
            # For randomness tests, use run-specific seed to preserve flakiness
            run_seed = (seed * 1000) + run_number
            self.set_random_seeds(run_seed)
        else:
            self.set_random_seeds(seed)
        
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
        
        # Parse results
        if output_file.exists():
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)
                
                summary = data.get('summary', {})
                passed = summary.get('passed', 0)
                total = summary.get('total', 1)
                pass_rate = passed / total if total > 0 else None
                
                return {
                    'run_number': run_number,
                    'seed': seed,
                    'markers': markers,
                    'execution_time': execution_time,
                    'pass_rate': pass_rate,
                    'tests_passed': passed,
                    'tests_total': total,
                    'return_code': result.returncode,
                    'output_file': str(output_file)
                }
            except Exception as e:
                if self.config.verbose:
                    print(f"Warning: Failed to parse {output_file}: {e}")
        
        return {
            'run_number': run_number,
            'seed': seed,
            'markers': markers,
            'execution_time': execution_time,
            'pass_rate': None,
            'tests_passed': 0,
            'tests_total': 0,
            'return_code': result.returncode,
            'output_file': str(output_file)
        }
    
    def _calculate_flakiness_index(self, results: List[Dict]) -> float:
        """Calculate flakiness index based on pass rate variability"""
        if not results:
            return 0.0
        
        pass_rates = [r['pass_rate'] for r in results if r['pass_rate'] is not None]
        if not pass_rates:
            return 0.0
        
        # Flakiness index: coefficient of variation of pass rates
        # Higher values indicate more flaky behavior
        mean_rate = np.mean(pass_rates)
        std_rate = np.std(pass_rates)
        
        if mean_rate == 0:
            return 1.0 if std_rate > 0 else 0.0
        
        return std_rate / mean_rate
    
    def _check_mitigation_dependencies(self) -> bool:
        """Check if mitigation dependencies are available"""
        required_packages = ['pytest-rerunfailures', 'pytest-forked']
        
        for package in required_packages:
            try:
                subprocess.run([sys.executable, "-c", f"import {package.replace('-', '_')}"], 
                             check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print(f"❌ Missing dependency: {package}")
                print(f"📦 Install with: pip install {package}")
                return False
        
        return True
    
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
        
        return self._parse_mitigation_result(output_file, run_number, execution_time, result.returncode)
    
    def _run_mocking_strategy(self, run_number: int) -> Dict:
        """Execute mocking mitigation strategy"""
        output_file = self.output_dir / f"mitigation_mocking_run_{run_number:03d}.json"
        
        # Create temporary conftest with mocks
        conftest_content = '''"""
Temporary configuration with comprehensive mocking
"""
import pytest
from unittest.mock import patch, MagicMock
import random


@pytest.fixture(autouse=True)
def mock_flaky_dependencies():
    """Mock all flaky dependencies"""
    
    # Mock random for randomness tests
    with patch('random.random') as mock_random:
        mock_random.return_value = 0.8  # Always pass randomness tests
        
        # Mock external API
        with patch('tests.test_flaky_external.MockExternalAPI.get_user_data') as mock_api:
            mock_api.return_value = {"id": 123, "name": "MockUser", "active": True}
            
            # Mock Database
            with patch('tests.test_flaky_external.MockDatabase.connect') as mock_db_connect:
                mock_db_connect.return_value = True
                
                with patch('tests.test_flaky_external.MockDatabase.query') as mock_db_query:
                    mock_db_query.return_value = [{"id": 1, "data": "mocked"}]
                    
                    # Mock time-sensitive operations
                    with patch('time.sleep') as mock_sleep:
                        mock_sleep.return_value = None  # Instant execution
                        
                        yield
'''
        
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
            
            return self._parse_mitigation_result(output_file, run_number, execution_time, result.returncode)
            
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
        
        return self._parse_mitigation_result(output_file, run_number, execution_time, result.returncode)
    
    def _run_combined_strategy(self, run_number: int) -> Dict:
        """Execute combined mitigation strategy"""
        output_file = self.output_dir / f"mitigation_combined_run_{run_number:03d}.json"
        
        # Create temporary conftest with mocks
        conftest_content = '''"""
Temporary configuration with comprehensive mocking for combined strategy
"""
import pytest
from unittest.mock import patch, MagicMock
import random


@pytest.fixture(autouse=True)
def mock_flaky_dependencies():
    """Mock all flaky dependencies for combined strategy"""
    
    # Mock random for randomness tests
    with patch('random.random') as mock_random:
        mock_random.return_value = 0.8  # Always pass randomness tests
        
        # Mock external API
        with patch('tests.test_flaky_external.MockExternalAPI.get_user_data') as mock_api:
            mock_api.return_value = {"id": 123, "name": "MockUser", "active": True}
            
            # Mock Database
            with patch('tests.test_flaky_external.MockDatabase.connect') as mock_db_connect:
                mock_db_connect.return_value = True
                
                with patch('tests.test_flaky_external.MockDatabase.query') as mock_db_query:
                    mock_db_query.return_value = [{"id": 1, "data": "mocked"}]
                    
                    # Mock time-sensitive operations
                    with patch('time.sleep') as mock_sleep:
                        mock_sleep.return_value = None  # Instant execution
                        
                        yield
'''
        
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
            
            return self._parse_mitigation_result(output_file, run_number, execution_time, result.returncode)
            
        finally:
            if conftest_path.exists():
                conftest_path.unlink()
    
    def _parse_mitigation_result(self, output_file: Path, run_number: int, execution_time: float, return_code: int) -> Dict:
        """Parse mitigation strategy results"""
        if output_file.exists():
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)
                
                summary = data.get('summary', {})
                passed = summary.get('passed', 0)
                total = summary.get('total', 1)
                pass_rate = passed / total if total > 0 else None
                
                return {
                    'run_number': run_number,
                    'execution_time': execution_time,
                    'pass_rate': pass_rate,
                    'tests_passed': passed,
                    'tests_total': total,
                    'return_code': return_code,
                    'output_file': str(output_file)
                }
            except Exception as e:
                if self.config.verbose:
                    print(f"Warning: Failed to parse {output_file}: {e}")
        
        return {
            'run_number': run_number,
            'execution_time': execution_time,
            'pass_rate': None,
            'tests_passed': 0,
            'tests_total': 0,
            'return_code': return_code,
            'output_file': str(output_file)
        }
    
    def _analyze_flakiness_types(self) -> Dict:
        """Analyze the 5 types of flakiness based on baseline results"""
        print("🔍 Analyzing flakiness types...")
        
        flakiness_analysis = {}
        
        for flaky_type in ['randomness', 'timeout', 'order', 'external', 'race']:
            if flaky_type in self.baseline_results:
                baseline_data = self.baseline_results[flaky_type]
                profile = self.flakiness_profiles[flaky_type]
                
                # Calculate actual metrics
                actual_pass_rate = baseline_data['avg_pass_rate']
                flakiness_index = baseline_data['flakiness_index']
                
                # Compare with expected profile
                deviation_from_expected = abs(actual_pass_rate - profile.typical_pass_rate)
                
                flakiness_analysis[flaky_type] = {
                    'profile': profile.__dict__,
                    'observed_metrics': {
                        'avg_pass_rate': actual_pass_rate,
                        'flakiness_index': flakiness_index,
                        'total_runs': baseline_data['total_runs'],
                        'valid_runs': baseline_data['valid_runs']
                    },
                    'classification': {
                        'severity': self._classify_severity(flakiness_index),
                        'predictability': self._classify_predictability(baseline_data['std_pass_rate']),
                        'deviation_from_expected': deviation_from_expected
                    }
                }
        
        return flakiness_analysis
    
    def _analyze_mitigation_effectiveness(self) -> Dict:
        """Analyze effectiveness of each mitigation strategy"""
        print("🎯 Analyzing mitigation effectiveness...")
        
        if not self.mitigation_results:
            return {}
        
        # Get baseline flaky test performance
        all_flaky_baseline = self.baseline_results.get('all_flaky', {})
        baseline_pass_rate = all_flaky_baseline.get('avg_pass_rate', 0)
        baseline_execution_time = np.mean([r['execution_time'] for r in all_flaky_baseline.get('results', []) if 'execution_time' in r])
        
        effectiveness_analysis = {}
        
        for strategy_name, strategy_data in self.mitigation_results.items():
            strategy_pass_rate = strategy_data['avg_pass_rate']
            strategy_execution_time = strategy_data['avg_execution_time']
            
            # Calculate effectiveness metrics
            improvement_absolute = strategy_pass_rate - baseline_pass_rate
            improvement_relative = (improvement_absolute / baseline_pass_rate * 100) if baseline_pass_rate > 0 else 0
            
            # Calculate overhead
            time_overhead = ((strategy_execution_time - baseline_execution_time) / baseline_execution_time * 100) if baseline_execution_time > 0 else 0
            
            # Calculate cost-effectiveness ratio
            cost_effectiveness = improvement_relative / max(time_overhead, 1) if time_overhead > 0 else improvement_relative
            
            effectiveness_analysis[strategy_name] = {
                'pass_rate_improvement': {
                    'absolute': improvement_absolute,
                    'relative_percent': improvement_relative
                },
                'performance_impact': {
                    'time_overhead_percent': time_overhead,
                    'absolute_time_increase': strategy_execution_time - baseline_execution_time
                },
                'cost_effectiveness_ratio': cost_effectiveness,
                'effectiveness_score': self._calculate_effectiveness_score(improvement_relative, time_overhead)
            }
        
        return effectiveness_analysis
    
    def _analyze_cost_benefit(self) -> Dict:
        """Analyze cost-benefit for each mitigation strategy"""
        print("💰 Analyzing cost-benefit...")
        
        cost_benefit = {}
        
        # Define implementation costs (relative scale 1-10)
        implementation_costs = {
            'retries': 2,      # Easy to configure
            'mocking': 6,      # Requires understanding dependencies
            'isolation': 4,    # Moderate setup complexity
            'combined': 8      # Complex to implement properly
        }
        
        # Define maintenance costs (relative scale 1-10)
        maintenance_costs = {
            'retries': 1,      # Very low maintenance
            'mocking': 7,      # High - mocks need updating
            'isolation': 3,    # Low maintenance
            'combined': 9      # High maintenance complexity
        }
        
        for strategy_name in self.mitigation_results.keys():
            effectiveness = self.analysis_results.get('mitigation_effectiveness', {}).get(strategy_name, {})
            
            # Get effectiveness score
            effectiveness_score = effectiveness.get('effectiveness_score', 0)
            improvement = effectiveness.get('pass_rate_improvement', {}).get('relative_percent', 0)
            overhead = effectiveness.get('performance_impact', {}).get('time_overhead_percent', 0)
            
            # Calculate total cost
            impl_cost = implementation_costs.get(strategy_name, 5)
            maint_cost = maintenance_costs.get(strategy_name, 5)
            total_cost = impl_cost + maint_cost + (overhead / 10)  # Include performance overhead in cost
            
            # Calculate benefit
            benefit = improvement * 10  # Scale improvement to benefit score
            
            # Calculate ROI
            roi = (benefit - total_cost) / total_cost if total_cost > 0 else 0
            
            cost_benefit[strategy_name] = {
                'costs': {
                    'implementation': impl_cost,
                    'maintenance': maint_cost,
                    'performance_overhead': overhead / 10,
                    'total': total_cost
                },
                'benefits': {
                    'improvement_score': benefit,
                    'effectiveness_score': effectiveness_score
                },
                'roi': roi,
                'recommendation': self._generate_strategy_recommendation(strategy_name, roi, effectiveness_score)
            }
        
        return cost_benefit
    
    def _analyze_statistical_significance(self) -> Dict:
        """Analyze statistical significance of results"""
        print("📈 Analyzing statistical significance...")
        
        # This is a simplified analysis - in a real study you'd use proper statistical tests
        significance_analysis = {
            'baseline_variability': {},
            'mitigation_improvements': {},
            'confidence_intervals': {}
        }
        
        # Analyze baseline variability
        for test_type, data in self.baseline_results.items():
            if test_type != 'stable_only':
                results = data.get('results', [])
                pass_rates = [r['pass_rate'] for r in results if r['pass_rate'] is not None]
                
                if pass_rates:
                    confidence_interval = np.percentile(pass_rates, [2.5, 97.5])
                    significance_analysis['baseline_variability'][test_type] = {
                        'mean': np.mean(pass_rates),
                        'std': np.std(pass_rates),
                        'confidence_interval_95': confidence_interval.tolist(),
                        'sample_size': len(pass_rates)
                    }
        
        return significance_analysis
    
    def _generate_recommendations(self) -> Dict:
        """Generate practical recommendations for developers"""
        print("📋 Generating recommendations...")
        
        recommendations = {
            'by_flakiness_type': {},
            'by_scenario': {},
            'general_guidelines': [],
            'implementation_priorities': []
        }
        
        # Recommendations by flakiness type
        for flaky_type, profile in self.flakiness_profiles.items():
            best_strategy = max(profile.mitigation_effectiveness.keys(), 
                              key=lambda k: profile.mitigation_effectiveness[k])
            
            recommendations['by_flakiness_type'][flaky_type] = {
                'primary_recommendation': best_strategy,
                'effectiveness_expected': profile.mitigation_effectiveness[best_strategy],
                'rationale': f"Best suited for {profile.failure_mechanism.lower()}",
                'implementation_notes': self._get_implementation_notes(flaky_type, best_strategy)
            }
        
        # Scenario-based recommendations
        recommendations['by_scenario'] = {
            'high_resource_constraints': {
                'recommended_strategy': 'retries',
                'rationale': 'Low implementation and maintenance cost',
                'trade_offs': 'Moderate effectiveness but minimal overhead'
            },
            'external_dependencies': {
                'recommended_strategy': 'mocking',
                'rationale': 'Eliminates external failure points',
                'trade_offs': 'Higher maintenance but very effective'
            },
            'concurrent_testing': {
                'recommended_strategy': 'isolation',
                'rationale': 'Prevents race conditions and state sharing',
                'trade_offs': 'Slower execution but reliable results'
            },
            'comprehensive_solution': {
                'recommended_strategy': 'combined',
                'rationale': 'Maximum effectiveness across all flakiness types',
                'trade_offs': 'Highest cost but best results'
            }
        }
        
        # General guidelines
        recommendations['general_guidelines'] = [
            "Start with retries for quick wins with minimal investment",
            "Identify root causes of flakiness before choosing mitigation strategy",
            "Mock external dependencies in CI/CD pipelines",
            "Use test isolation for tests with shared state",
            "Monitor test stability metrics continuously",
            "Invest in fixing root causes rather than just mitigating symptoms"
        ]
        
        # Implementation priorities
        if self.analysis_results.get('cost_benefit_analysis'):
            cost_benefit = self.analysis_results['cost_benefit_analysis']
            sorted_strategies = sorted(cost_benefit.items(), 
                                     key=lambda x: x[1]['roi'], reverse=True)
            
            recommendations['implementation_priorities'] = [
                {
                    'priority': i + 1,
                    'strategy': strategy,
                    'roi': data['roi'],
                    'justification': data['recommendation']
                }
                for i, (strategy, data) in enumerate(sorted_strategies)
            ]
        
        return recommendations
    
    def _classify_severity(self, flakiness_index: float) -> str:
        """Classify flakiness severity based on index"""
        if flakiness_index < 0.1:
            return "low"
        elif flakiness_index < 0.3:
            return "moderate"
        elif flakiness_index < 0.6:
            return "high"
        else:
            return "severe"
    
    def _classify_predictability(self, std_pass_rate: float) -> str:
        """Classify predictability based on standard deviation"""
        if std_pass_rate < 0.1:
            return "highly_predictable"
        elif std_pass_rate < 0.2:
            return "moderately_predictable"
        elif std_pass_rate < 0.3:
            return "low_predictability"
        else:
            return "unpredictable"
    
    def _calculate_effectiveness_score(self, improvement_percent: float, overhead_percent: float) -> float:
        """Calculate overall effectiveness score"""
        # Weighted score: improvement is more important than overhead
        improvement_weight = 0.7
        overhead_weight = 0.3
        
        # Normalize improvement (0-100) to 0-1 scale
        improvement_score = min(improvement_percent / 100, 1.0)
        
        # Normalize overhead penalty (higher overhead = lower score)
        overhead_penalty = min(overhead_percent / 100, 1.0)
        
        effectiveness = (improvement_score * improvement_weight) - (overhead_penalty * overhead_weight)
        return max(effectiveness, 0.0)  # Ensure non-negative
    
    def _generate_strategy_recommendation(self, strategy: str, roi: float, effectiveness: float) -> str:
        """Generate recommendation for a specific strategy"""
        if roi > 2.0 and effectiveness > 0.5:
            return f"Highly recommended - excellent ROI and effectiveness"
        elif roi > 1.0 and effectiveness > 0.3:
            return f"Recommended - good balance of cost and benefit"
        elif effectiveness > 0.6:
            return f"Consider if effectiveness is priority over cost"
        elif roi > 0.5:
            return f"Consider for cost-sensitive environments"
        else:
            return f"Not recommended - poor cost-benefit ratio"
    
    def _get_implementation_notes(self, flaky_type: str, strategy: str) -> str:
        """Get implementation notes for specific flakiness type and strategy"""
        notes = {
            ('randomness', 'mocking'): "Mock random number generators with fixed values",
            ('randomness', 'retries'): "Multiple attempts may eventually succeed due to randomness",
            ('timeout', 'isolation'): "Run tests in isolated processes to reduce resource contention",
            ('timeout', 'retries'): "Retry failed tests as timing issues may be transient",
            ('order', 'isolation'): "Essential for preventing state sharing between tests",
            ('order', 'mocking'): "Mock shared resources to prevent state conflicts",
            ('external', 'mocking'): "Mock all external API calls and services",
            ('external', 'retries'): "Retry on network failures or service unavailability",
            ('race', 'isolation'): "Run tests in separate processes to eliminate race conditions",
            ('race', 'mocking'): "Mock concurrent operations to ensure deterministic behavior"
        }
        
        return notes.get((flaky_type, strategy), f"Apply {strategy} strategy for {flaky_type} tests")
    
    def _create_visualizations(self):
        """Create comprehensive visualizations"""
        print("📊 Creating visualizations...")
        
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Flakiness Classification Overview
        self._create_flakiness_overview_plot()
        
        # 2. Mitigation Effectiveness Comparison
        self._create_mitigation_effectiveness_plot()
        
        # 3. Cost-Benefit Analysis
        self._create_cost_benefit_plot()
        
        # 4. Detailed Performance Analysis
        self._create_performance_analysis_plot()
    
    def _create_flakiness_overview_plot(self):
        """Create flakiness classification overview plot"""
        if not self.analysis_results.get('flakiness_classification'):
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Flakiness Classification Analysis', fontsize=16, fontweight='bold')
        
        flakiness_data = self.analysis_results['flakiness_classification']
        
        # Extract data for plotting
        types = []
        pass_rates = []
        flakiness_indices = []
        severities = []
        
        for flaky_type, data in flakiness_data.items():
            types.append(flaky_type.replace('_', ' ').title())
            pass_rates.append(data['observed_metrics']['avg_pass_rate'])
            flakiness_indices.append(data['observed_metrics']['flakiness_index'])
            severities.append(data['classification']['severity'])
        
        # Pass rates by type
        bars1 = axes[0,0].bar(types, pass_rates, color='skyblue', alpha=0.7)
        axes[0,0].set_title('Average Pass Rate by Flakiness Type')
        axes[0,0].set_ylabel('Pass Rate')
        axes[0,0].set_ylim(0, 1)
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars1, pass_rates):
            axes[0,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                          f'{value:.2f}', ha='center', va='bottom')
        
        # Flakiness indices
        bars2 = axes[0,1].bar(types, flakiness_indices, color='lightcoral', alpha=0.7)
        axes[0,1].set_title('Flakiness Index by Type')
        axes[0,1].set_ylabel('Flakiness Index')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # Severity distribution
        severity_counts = pd.Series(severities).value_counts()
        axes[1,0].pie(severity_counts.values, labels=severity_counts.index, autopct='%1.1f%%')
        axes[1,0].set_title('Severity Distribution')
        
        # Expected vs Observed Pass Rates
        expected_rates = [self.flakiness_profiles[flaky_type].typical_pass_rate for flaky_type in flakiness_data.keys()]
        
        x = np.arange(len(types))
        width = 0.35
        
        axes[1,1].bar(x - width/2, expected_rates, width, label='Expected', alpha=0.7)
        axes[1,1].bar(x + width/2, pass_rates, width, label='Observed', alpha=0.7)
        axes[1,1].set_title('Expected vs Observed Pass Rates')
        axes[1,1].set_ylabel('Pass Rate')
        axes[1,1].set_xticks(x)
        axes[1,1].set_xticklabels(types, rotation=45)
        axes[1,1].legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'flakiness_classification.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_mitigation_effectiveness_plot(self):
        """Create mitigation effectiveness comparison plot"""
        if not self.analysis_results.get('mitigation_effectiveness'):
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Mitigation Strategy Effectiveness Analysis', fontsize=16, fontweight='bold')
        
        effectiveness_data = self.analysis_results['mitigation_effectiveness']
        
        strategies = list(effectiveness_data.keys())
        improvements = [data['pass_rate_improvement']['relative_percent'] for data in effectiveness_data.values()]
        overheads = [data['performance_impact']['time_overhead_percent'] for data in effectiveness_data.values()]
        effectiveness_scores = [data['effectiveness_score'] for data in effectiveness_data.values()]
        
        # Improvement comparison
        bars1 = axes[0,0].bar(strategies, improvements, color='lightgreen', alpha=0.7)
        axes[0,0].set_title('Pass Rate Improvement by Strategy')
        axes[0,0].set_ylabel('Improvement (%)')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars1, improvements):
            axes[0,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                          f'{value:.1f}%', ha='center', va='bottom')
        
        # Performance overhead
        bars2 = axes[0,1].bar(strategies, overheads, color='orange', alpha=0.7)
        axes[0,1].set_title('Performance Overhead by Strategy')
        axes[0,1].set_ylabel('Overhead (%)')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # Effectiveness scores
        bars3 = axes[1,0].bar(strategies, effectiveness_scores, color='purple', alpha=0.7)
        axes[1,0].set_title('Overall Effectiveness Score')
        axes[1,0].set_ylabel('Effectiveness Score')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Scatter plot: Improvement vs Overhead
        colors = ['red', 'blue', 'green', 'orange']
        for i, strategy in enumerate(strategies):
            axes[1,1].scatter(overheads[i], improvements[i], 
                            s=effectiveness_scores[i]*500, 
                            c=colors[i], alpha=0.7, label=strategy)
        
        axes[1,1].set_xlabel('Performance Overhead (%)')
        axes[1,1].set_ylabel('Pass Rate Improvement (%)')
        axes[1,1].set_title('Improvement vs Overhead (size = effectiveness)')
        axes[1,1].legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'mitigation_effectiveness.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_cost_benefit_plot(self):
        """Create cost-benefit analysis plot"""
        if not self.analysis_results.get('cost_benefit_analysis'):
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Cost-Benefit Analysis', fontsize=16, fontweight='bold')
        
        cost_benefit_data = self.analysis_results['cost_benefit_analysis']
        
        strategies = list(cost_benefit_data.keys())
        total_costs = [data['costs']['total'] for data in cost_benefit_data.values()]
        benefits = [data['benefits']['improvement_score'] for data in cost_benefit_data.values()]
        rois = [data['roi'] for data in cost_benefit_data.values()]
        
        # Cost breakdown
        impl_costs = [data['costs']['implementation'] for data in cost_benefit_data.values()]
        maint_costs = [data['costs']['maintenance'] for data in cost_benefit_data.values()]
        perf_costs = [data['costs']['performance_overhead'] for data in cost_benefit_data.values()]
        
        x = np.arange(len(strategies))
        width = 0.6
        
        axes[0,0].bar(x, impl_costs, width, label='Implementation', color='lightblue')
        axes[0,0].bar(x, maint_costs, width, bottom=impl_costs, label='Maintenance', color='lightcoral')
        axes[0,0].bar(x, perf_costs, width, bottom=np.array(impl_costs) + np.array(maint_costs), 
                     label='Performance', color='lightyellow')
        
        axes[0,0].set_title('Cost Breakdown by Strategy')
        axes[0,0].set_ylabel('Cost Score')
        axes[0,0].set_xticks(x)
        axes[0,0].set_xticklabels(strategies, rotation=45)
        axes[0,0].legend()
        
        # ROI comparison
        colors = ['green' if roi > 1 else 'red' if roi < 0 else 'orange' for roi in rois]
        bars2 = axes[0,1].bar(strategies, rois, color=colors, alpha=0.7)
        axes[0,1].set_title('Return on Investment (ROI)')
        axes[0,1].set_ylabel('ROI')
        axes[0,1].tick_params(axis='x', rotation=45)
        axes[0,1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[0,1].axhline(y=1, color='green', linestyle='--', alpha=0.5, label='Break-even')
        
        # Cost vs Benefit scatter
        for i, strategy in enumerate(strategies):
            axes[1,0].scatter(total_costs[i], benefits[i], s=100, label=strategy)
            axes[1,0].annotate(strategy, (total_costs[i], benefits[i]), 
                             xytext=(5, 5), textcoords='offset points')
        
        axes[1,0].set_xlabel('Total Cost Score')
        axes[1,0].set_ylabel('Benefit Score')
        axes[1,0].set_title('Cost vs Benefit Analysis')
        
        # ROI ranking
        roi_ranking = sorted(zip(strategies, rois), key=lambda x: x[1], reverse=True)
        ranked_strategies, ranked_rois = zip(*roi_ranking)
        
        colors_ranked = ['green' if roi > 1 else 'red' if roi < 0 else 'orange' for roi in ranked_rois]
        axes[1,1].barh(range(len(ranked_strategies)), ranked_rois, color=colors_ranked, alpha=0.7)
        axes[1,1].set_yticks(range(len(ranked_strategies)))
        axes[1,1].set_yticklabels(ranked_strategies)
        axes[1,1].set_xlabel('ROI')
        axes[1,1].set_title('Strategy Ranking by ROI')
        axes[1,1].axvline(x=0, color='black', linestyle='--', alpha=0.5)
        axes[1,1].axvline(x=1, color='green', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'cost_benefit_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_performance_analysis_plot(self):
        """Create detailed performance analysis plot"""
        if not self.baseline_results or not self.mitigation_results:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Detailed Performance Analysis', fontsize=16, fontweight='bold')
        
        # Baseline performance by flakiness type
        baseline_types = []
        baseline_pass_rates = []
        baseline_exec_times = []
        
        for test_type, data in self.baseline_results.items():
            if test_type != 'stable_only':
                baseline_types.append(test_type.replace('_', ' ').title())
                baseline_pass_rates.append(data['avg_pass_rate'])
                
                # Calculate average execution time
                results = data.get('results', [])
                exec_times = [r.get('execution_time', 0) for r in results if 'execution_time' in r]
                baseline_exec_times.append(np.mean(exec_times) if exec_times else 0)
        
        # Baseline pass rates
        axes[0,0].bar(baseline_types, baseline_pass_rates, color='lightcoral', alpha=0.7)
        axes[0,0].set_title('Baseline Pass Rates by Flakiness Type')
        axes[0,0].set_ylabel('Pass Rate')
        axes[0,0].set_ylim(0, 1)
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Baseline execution times
        axes[0,1].bar(baseline_types, baseline_exec_times, color='lightblue', alpha=0.7)
        axes[0,1].set_title('Baseline Execution Times by Type')
        axes[0,1].set_ylabel('Execution Time (seconds)')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # Mitigation strategy comparison
        if self.mitigation_results:
            mit_strategies = list(self.mitigation_results.keys())
            mit_pass_rates = [data['avg_pass_rate'] for data in self.mitigation_results.values()]
            mit_exec_times = [data['avg_execution_time'] for data in self.mitigation_results.values()]
            
            # Add baseline for comparison
            baseline_flaky = self.baseline_results.get('all_flaky', {})
            if baseline_flaky:
                mit_strategies.insert(0, 'baseline')
                mit_pass_rates.insert(0, baseline_flaky['avg_pass_rate'])
                baseline_exec_time = np.mean([r.get('execution_time', 0) for r in baseline_flaky.get('results', [])])
                mit_exec_times.insert(0, baseline_exec_time)
            
            # Pass rate comparison
            colors = ['red'] + ['green', 'blue', 'orange', 'purple'][:len(mit_strategies)-1]
            axes[1,0].bar(mit_strategies, mit_pass_rates, color=colors, alpha=0.7)
            axes[1,0].set_title('Pass Rate: Baseline vs Mitigation Strategies')
            axes[1,0].set_ylabel('Pass Rate')
            axes[1,0].set_ylim(0, 1)
            axes[1,0].tick_params(axis='x', rotation=45)
            
            # Execution time comparison
            axes[1,1].bar(mit_strategies, mit_exec_times, color=colors, alpha=0.7)
            axes[1,1].set_title('Execution Time: Baseline vs Mitigation Strategies')
            axes[1,1].set_ylabel('Execution Time (seconds)')
            axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'performance_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_text_report(self) -> str:
        """Generate comprehensive text report"""
        report_lines = []
        
        # Header
        report_lines.extend([
            "=" * 80,
            "COMPREHENSIVE FLAKY TEST MITIGATION STUDY - FINAL REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Study Duration: {(time.time() - self.study_start_time) / 60:.1f} minutes",
            f"Framework: Synthetic Flaky Python",
            "",
            "EXECUTIVE SUMMARY",
            "-" * 40,
        ])
        
        # Executive summary
        if self.analysis_results.get('cost_benefit_analysis'):
            best_strategy = max(self.analysis_results['cost_benefit_analysis'].items(),
                              key=lambda x: x[1]['roi'])
            
            report_lines.extend([
                f"This study analyzed 5 types of flakiness and 4 mitigation strategies.",
                f"Best overall strategy: {best_strategy[0].upper()} (ROI: {best_strategy[1]['roi']:.2f})",
                f"Total experiments executed: {sum(data.get('total_runs', 0) for data in self.baseline_results.values()) + sum(data.get('total_runs', 0) for data in self.mitigation_results.values())}",
                ""
            ])
        
        # Flakiness classification
        if self.analysis_results.get('flakiness_classification'):
            report_lines.extend([
                "FLAKINESS CLASSIFICATION ANALYSIS",
                "-" * 40,
            ])
            
            for flaky_type, data in self.analysis_results['flakiness_classification'].items():
                metrics = data['observed_metrics']
                classification = data['classification']
                
                report_lines.extend([
                    f"{flaky_type.upper().replace('_', ' ')}:",
                    f"  • Pass Rate: {metrics['avg_pass_rate']:.1%} (flakiness index: {metrics['flakiness_index']:.3f})",
                    f"  • Severity: {classification['severity'].replace('_', ' ').title()}",
                    f"  • Predictability: {classification['predictability'].replace('_', ' ').title()}",
                    f"  • Mechanism: {data['profile']['failure_mechanism']}",
                    ""
                ])
        
        # Mitigation effectiveness
        if self.analysis_results.get('mitigation_effectiveness'):
            report_lines.extend([
                "MITIGATION STRATEGY EFFECTIVENESS",
                "-" * 40,
            ])
            
            for strategy, data in self.analysis_results['mitigation_effectiveness'].items():
                improvement = data['pass_rate_improvement']['relative_percent']
                overhead = data['performance_impact']['time_overhead_percent']
                score = data['effectiveness_score']
                
                report_lines.extend([
                    f"{strategy.upper()}:",
                    f"  • Pass Rate Improvement: {improvement:+.1f}%",
                    f"  • Performance Overhead: {overhead:+.1f}%",
                    f"  • Effectiveness Score: {score:.3f}",
                    ""
                ])
        
        # Cost-benefit analysis
        if self.analysis_results.get('cost_benefit_analysis'):
            report_lines.extend([
                "COST-BENEFIT ANALYSIS",
                "-" * 40,
            ])
            
            for strategy, data in self.analysis_results['cost_benefit_analysis'].items():
                roi = data['roi']
                recommendation = data['recommendation']
                
                report_lines.extend([
                    f"{strategy.upper()}:",
                    f"  • ROI: {roi:.2f}",
                    f"  • Recommendation: {recommendation}",
                    ""
                ])
        
        # Recommendations
        if self.analysis_results.get('recommendations'):
            recommendations = self.analysis_results['recommendations']
            
            report_lines.extend([
                "PRACTICAL RECOMMENDATIONS",
                "-" * 40,
            ])
            
            # Implementation priorities
            if recommendations.get('implementation_priorities'):
                report_lines.append("Implementation Priority Ranking:")
                for priority in recommendations['implementation_priorities']:
                    report_lines.append(f"  {priority['priority']}. {priority['strategy'].upper()} (ROI: {priority['roi']:.2f})")
                report_lines.append("")
            
            # By flakiness type
            if recommendations.get('by_flakiness_type'):
                report_lines.append("Recommendations by Flakiness Type:")
                for flaky_type, rec in recommendations['by_flakiness_type'].items():
                    report_lines.extend([
                        f"  • {flaky_type.replace('_', ' ').title()}: Use {rec['primary_recommendation'].upper()}",
                        f"    Expected effectiveness: {rec['effectiveness_expected']:.1%}",
                        f"    Notes: {rec['implementation_notes']}",
                    ])
                report_lines.append("")
            
            # General guidelines
            if recommendations.get('general_guidelines'):
                report_lines.append("General Guidelines:")
                for guideline in recommendations['general_guidelines']:
                    report_lines.append(f"  • {guideline}")
                report_lines.append("")
        
        # Technical appendix
        report_lines.extend([
            "TECHNICAL APPENDIX",
            "-" * 40,
            f"Study Configuration:",
            f"  • Baseline runs per type: {self.config.baseline_runs}",
            f"  • Mitigation runs per strategy: {self.config.mitigation_runs}",
            f"  • Random seeds: {self.config.seeds}",
            f"  • Output directory: {self.output_dir}",
            "",
            "Files Generated:",
            "  • comprehensive_study_report.txt - This report",
            "  • comprehensive_study_data.json - Complete raw data",
            "  • flakiness_classification.png - Flakiness analysis visualization",
            "  • mitigation_effectiveness.png - Strategy effectiveness comparison",
            "  • cost_benefit_analysis.png - Cost-benefit visualization",
            "  • performance_analysis.png - Performance metrics",
            "",
            "=" * 80,
        ])
        
        report_content = "\n".join(report_lines)
        
        # Save report
        report_file = self.output_dir / "comprehensive_study_report.txt"
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        return report_content
    
    def _save_all_data(self):
        """Save all experimental data and analysis results"""
        print("💾 Saving all data...")
        
        complete_data = {
            'study_metadata': self.study_metadata,
            'configuration': self.config.__dict__,
            'baseline_results': self.baseline_results,
            'mitigation_results': self.mitigation_results,
            'analysis_results': self.analysis_results,
            'flakiness_profiles': {k: v.__dict__ for k, v in self.flakiness_profiles.items()},
            'study_duration_minutes': (time.time() - self.study_start_time) / 60
        }
        
        # Save complete data as JSON
        data_file = self.output_dir / "comprehensive_study_data.json"
        with open(data_file, 'w') as f:
            json.dump(complete_data, f, indent=2, default=str)
        
        # Save CSV summaries for easy analysis
        self._save_csv_summaries()
    
    def _save_csv_summaries(self):
        """Save CSV summaries for easy analysis"""
        # Baseline summary
        if self.baseline_results:
            baseline_summary = []
            for test_type, data in self.baseline_results.items():
                baseline_summary.append({
                    'test_type': test_type,
                    'avg_pass_rate': data.get('avg_pass_rate', 0),
                    'std_pass_rate': data.get('std_pass_rate', 0),
                    'flakiness_index': data.get('flakiness_index', 0),
                    'total_runs': data.get('total_runs', 0),
                    'valid_runs': data.get('valid_runs', 0),
                    'duration': data.get('duration', 0)
                })
            
            pd.DataFrame(baseline_summary).to_csv(
                self.output_dir / 'baseline_summary.csv', index=False)
        
        # Mitigation summary
        if self.mitigation_results:
            mitigation_summary = []
            for strategy, data in self.mitigation_results.items():
                mitigation_summary.append({
                    'strategy': strategy,
                    'avg_pass_rate': data.get('avg_pass_rate', 0),
                    'std_pass_rate': data.get('std_pass_rate', 0),
                    'avg_execution_time': data.get('avg_execution_time', 0),
                    'total_runs': data.get('total_runs', 0),
                    'valid_runs': data.get('valid_runs', 0),
                    'duration': data.get('duration', 0)
                })
            
            pd.DataFrame(mitigation_summary).to_csv(
                self.output_dir / 'mitigation_summary.csv', index=False)
    
    def _print_final_summary(self):
        """Print final summary to console"""
        total_duration = (time.time() - self.study_start_time) / 60
        
        print("\n" + "=" * 70)
        print("🎉 COMPREHENSIVE STUDY COMPLETED!")
        print("=" * 70)
        print(f"📊 Study Duration: {total_duration:.1f} minutes")
        print(f"📁 Results Directory: {self.output_dir}")
        print()
        
        # Key findings summary
        if self.analysis_results.get('cost_benefit_analysis'):
            # Best strategy by ROI
            best_roi = max(self.analysis_results['cost_benefit_analysis'].items(),
                          key=lambda x: x[1]['roi'])
            
            # Most effective strategy
            if self.analysis_results.get('mitigation_effectiveness'):
                best_effectiveness = max(self.analysis_results['mitigation_effectiveness'].items(),
                                       key=lambda x: x[1]['effectiveness_score'])
                
                print("🏆 KEY FINDINGS:")
                print(f"   Best ROI: {best_roi[0].upper()} (ROI: {best_roi[1]['roi']:.2f})")
                print(f"   Most Effective: {best_effectiveness[0].upper()} (Score: {best_effectiveness[1]['effectiveness_score']:.3f})")
        
        # Flakiness insights
        if self.analysis_results.get('flakiness_classification'):
            most_problematic = min(self.analysis_results['flakiness_classification'].items(),
                                 key=lambda x: x[1]['observed_metrics']['avg_pass_rate'])
            
            print(f"   Most Problematic Type: {most_problematic[0].replace('_', ' ').title()} ({most_problematic[1]['observed_metrics']['avg_pass_rate']:.1%} pass rate)")
        
        print()
        print("📋 Generated Files:")
        print(f"   📄 comprehensive_study_report.txt - Complete analysis report")
        print(f"   📊 comprehensive_study_data.json - All raw data and results")
        print(f"   📈 *.png - Visualization charts (4 files)")
        print(f"   📝 *.csv - Summary tables (2 files)")
        print()
        print("✅ Study complete! All data ready for publication and further analysis.")


def setup_args():
    """Setup command line arguments"""
    parser = argparse.ArgumentParser(description="Run comprehensive flaky test study")
    parser.add_argument("--baseline-runs", type=int, default=30,
                       help="Number of runs per baseline configuration (default: 30)")
    parser.add_argument("--mitigation-runs", type=int, default=10,
                       help="Number of runs per mitigation strategy (default: 10)")
    parser.add_argument("--output-dir", type=str, default="comprehensive_results",
                       help="Output directory (default: comprehensive_results)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--seeds", type=int, nargs='+', default=[42, 123, 999],
                       help="Random seeds for reproducibility (default: 42 123 999)")
    parser.add_argument("--skip-baseline", action="store_true",
                       help="Skip baseline experiments (use existing data)")
    parser.add_argument("--skip-mitigation", action="store_true",
                       help="Skip mitigation experiments (use existing data)")
    
    return parser.parse_args()


def main():
    """Main function to run comprehensive study"""
    print("🧪 SYNTHETIC FLAKY PYTHON - COMPREHENSIVE STUDY")
    print("=" * 70)
    print("Empirical Study of Flaky Test Mitigation Techniques")
    print("Framework: Reproducible with fixed seeds")
    print("Comparison: 4 mitigation techniques across 5 flakiness types")
    print()
    
    # Parse arguments
    args = setup_args()
    
    # Create configuration
    config = StudyConfiguration(
        baseline_runs=args.baseline_runs,
        mitigation_runs=args.mitigation_runs,
        seeds=args.seeds,
        output_dir=args.output_dir,
        verbose=args.verbose,
        skip_baseline=args.skip_baseline,
        skip_mitigation=args.skip_mitigation
    )
    
    print(f"Configuration:")
    print(f"  • Baseline runs per type: {config.baseline_runs}")
    print(f"  • Mitigation runs per strategy: {config.mitigation_runs}")
    print(f"  • Seeds: {config.seeds}")
    print(f"  • Output directory: {config.output_dir}")
    print(f"  • Skip baseline: {config.skip_baseline}")
    print(f"  • Skip mitigation: {config.skip_mitigation}")
    print()
    
    try:
        # Initialize study
        study = ComprehensiveStudy(config)
        
        # Execute study phases
        study.run_baseline_experiments()
        study.run_mitigation_experiments()
        study.analyze_results()
        study.generate_report()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Study interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during study: {e}")
        if config.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
