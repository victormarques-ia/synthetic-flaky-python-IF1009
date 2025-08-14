"""
Utility Helper Functions
========================

Shared utility functions used across the comprehensive study framework.
"""

import os
import sys
import json
import random
import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Tuple


def set_random_seeds(seed: int):
    """Set random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    os.environ['RANDOM_SEED'] = str(seed)


def check_mitigation_dependencies() -> bool:
    """Check if required dependencies are available"""
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


def parse_test_result(output_file: Path, run_number: int, execution_time: float, 
                     return_code: int, markers: str = None, seed: int = None) -> Dict:
    """Parse test execution results from JSON output file"""
    if output_file.exists():
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            summary = data.get('summary', {})
            passed = summary.get('passed', 0)
            total = summary.get('total', 1)
            pass_rate = passed / total if total > 0 else None
            
            result = {
                'run_number': run_number,
                'execution_time': execution_time,
                'pass_rate': pass_rate,
                'tests_passed': passed,
                'tests_total': total,
                'return_code': return_code,
                'output_file': str(output_file)
            }
            
            # Add optional metadata
            if markers:
                result['markers'] = markers
            if seed:
                result['seed'] = seed
                
            return result
            
        except Exception as e:
            print(f"Warning: Failed to parse {output_file}: {e}")
    
    # Return default result if parsing fails
    result = {
        'run_number': run_number,
        'execution_time': execution_time,
        'pass_rate': None,
        'tests_passed': 0,
        'tests_total': 0,
        'return_code': return_code,
        'output_file': str(output_file)
    }
    
    if markers:
        result['markers'] = markers
    if seed:
        result['seed'] = seed
        
    return result


def calculate_flakiness_index(results: list) -> float:
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


def calculate_effectiveness_score(improvement_percent: float, overhead_percent: float) -> float:
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


def generate_strategy_recommendation(strategy: str, roi: float, effectiveness: float) -> str:
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


def create_mock_conftest_content() -> str:
    """Generate content for temporary conftest.py with comprehensive mocking"""
    return '''"""
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


def safe_file_operation(operation, *args, **kwargs):
    """Safely perform file operations with error handling"""
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        print(f"Warning: File operation failed: {e}")
        return None


def validate_output_directory(output_dir: Path) -> Path:
    """Validate and create output directory if needed"""
    try:
        output_dir.mkdir(exist_ok=True)
        return output_dir
    except Exception as e:
        print(f"Warning: Could not create output directory {output_dir}: {e}")
        # Fallback to current directory
        fallback_dir = Path.cwd() / "study_results"
        fallback_dir.mkdir(exist_ok=True)
        return fallback_dir
