"""
Study Configuration Module
==========================

Configuration classes and data structures for the comprehensive flaky test study.
"""

from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path


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


# Study constants
FLAKINESS_TYPES = ['randomness', 'timeout', 'order', 'external', 'race']
MITIGATION_STRATEGIES = ['retries', 'mocking', 'isolation', 'combined']

# Default baseline configurations for experiments
BASELINE_CONFIGURATIONS = [
    {"name": "stable_only", "markers": "stable", "description": "Stable tests only (0% flaky)"},
    {"name": "randomness", "markers": "randomness", "description": "Randomness-based flaky tests"},
    {"name": "timeout", "markers": "timeout", "description": "Timeout-based flaky tests"},
    {"name": "order", "markers": "order", "description": "Order-dependent flaky tests"},
    {"name": "external", "markers": "external", "description": "External dependency flaky tests"},
    {"name": "race", "markers": "race", "description": "Race condition flaky tests"},
    {"name": "all_flaky", "markers": "flaky", "description": "All flaky tests combined"},
]

# Cost definitions for cost-benefit analysis (relative scale 1-10)
IMPLEMENTATION_COSTS = {
    'retries': 2,      # Easy to configure
    'mocking': 6,      # Requires understanding dependencies
    'isolation': 4,    # Moderate setup complexity
    'combined': 8      # Complex to implement properly
}

MAINTENANCE_COSTS = {
    'retries': 1,      # Very low maintenance
    'mocking': 7,      # High - mocks need updating
    'isolation': 3,    # Low maintenance
    'combined': 9      # High maintenance complexity
}
