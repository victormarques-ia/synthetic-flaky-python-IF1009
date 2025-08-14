"""
Flakiness Classification Module
===============================

Systematic classification and analysis of the 5 main types of flakiness.
"""

from typing import Dict
from config.study_config import FlakynessProfile


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
    
    @staticmethod
    def classify_severity(flakiness_index: float) -> str:
        """Classify flakiness severity based on index"""
        if flakiness_index < 0.1:
            return "low"
        elif flakiness_index < 0.3:
            return "moderate"
        elif flakiness_index < 0.6:
            return "high"
        else:
            return "severe"
    
    @staticmethod
    def classify_predictability(std_pass_rate: float) -> str:
        """Classify predictability based on standard deviation"""
        if std_pass_rate < 0.1:
            return "highly_predictable"
        elif std_pass_rate < 0.2:
            return "moderately_predictable"
        elif std_pass_rate < 0.3:
            return "low_predictability"
        else:
            return "unpredictable"
    
    @staticmethod
    def get_implementation_notes(flaky_type: str, strategy: str) -> str:
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
