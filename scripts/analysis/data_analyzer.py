"""
Data Analysis Module
====================

Comprehensive analysis of baseline and mitigation experiment results.
"""

from typing import Dict
import numpy as np

from config.study_config import IMPLEMENTATION_COSTS, MAINTENANCE_COSTS
from classification.flakiness_classifier import FlakynessClassifier
from utils.helpers import calculate_effectiveness_score, generate_strategy_recommendation


class DataAnalyzer:
    """Analyzes experimental data and generates insights"""
    
    def __init__(self):
        self.classifier = FlakynessClassifier()
        self.flakiness_profiles = self.classifier.get_flakiness_profiles()
    
    def analyze(self, baseline_results: Dict, mitigation_results: Dict) -> Dict:
        """Comprehensive analysis of all results"""
        print("📊 PHASE 3: COMPREHENSIVE ANALYSIS")
        print("=" * 50)
        print("Analyzing effectiveness, cost-benefit, and generating recommendations")
        print()
        
        analysis = {
            'flakiness_classification': self._analyze_flakiness_types(baseline_results),
            'mitigation_effectiveness': self._analyze_mitigation_effectiveness(baseline_results, mitigation_results),
            'cost_benefit_analysis': self._analyze_cost_benefit(baseline_results, mitigation_results),
            'statistical_significance': self._analyze_statistical_significance(baseline_results, mitigation_results),
            'recommendations': self._generate_recommendations(baseline_results, mitigation_results)
        }
        
        return analysis
    
    def _analyze_flakiness_types(self, baseline_results: Dict) -> Dict:
        """Analyze the 5 types of flakiness based on baseline results"""
        print("🔍 Analyzing flakiness types...")
        
        flakiness_analysis = {}
        
        for flaky_type in ['randomness', 'timeout', 'order', 'external', 'race']:
            if flaky_type in baseline_results:
                baseline_data = baseline_results[flaky_type]
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
                        'severity': self.classifier.classify_severity(flakiness_index),
                        'predictability': self.classifier.classify_predictability(baseline_data['std_pass_rate']),
                        'deviation_from_expected': deviation_from_expected
                    }
                }
        
        return flakiness_analysis
    
    def _analyze_mitigation_effectiveness(self, baseline_results: Dict, mitigation_results: Dict) -> Dict:
        """Analyze effectiveness of each mitigation strategy"""
        print("🎯 Analyzing mitigation effectiveness...")
        
        if not mitigation_results:
            return {}
        
        # Get baseline flaky test performance
        all_flaky_baseline = baseline_results.get('all_flaky', {})
        baseline_pass_rate = all_flaky_baseline.get('avg_pass_rate', 0)
        baseline_execution_time = np.mean([r['execution_time'] for r in all_flaky_baseline.get('results', []) if 'execution_time' in r])
        
        effectiveness_analysis = {}
        
        for strategy_name, strategy_data in mitigation_results.items():
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
                'effectiveness_score': calculate_effectiveness_score(improvement_relative, time_overhead)
            }
        
        return effectiveness_analysis
    
    def _analyze_cost_benefit(self, baseline_results: Dict, mitigation_results: Dict) -> Dict:
        """Analyze cost-benefit for each mitigation strategy"""
        print("💰 Analyzing cost-benefit...")
        
        cost_benefit = {}
        
        for strategy_name in mitigation_results.keys():
            # Get effectiveness data (will be available after analyze() runs)
            effectiveness = {}  # This will be populated by the main analysis
            
            # Get effectiveness score
            effectiveness_score = effectiveness.get('effectiveness_score', 0)
            improvement = effectiveness.get('pass_rate_improvement', {}).get('relative_percent', 0)
            overhead = effectiveness.get('performance_impact', {}).get('time_overhead_percent', 0)
            
            # Calculate total cost
            impl_cost = IMPLEMENTATION_COSTS.get(strategy_name, 5)
            maint_cost = MAINTENANCE_COSTS.get(strategy_name, 5)
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
                'recommendation': generate_strategy_recommendation(strategy_name, roi, effectiveness_score)
            }
        
        return cost_benefit
    
    def _analyze_statistical_significance(self, baseline_results: Dict, mitigation_results: Dict) -> Dict:
        """Analyze statistical significance of results"""
        print("📈 Analyzing statistical significance...")
        
        # This is a simplified analysis - in a real study you'd use proper statistical tests
        significance_analysis = {
            'baseline_variability': {},
            'mitigation_improvements': {},
            'confidence_intervals': {}
        }
        
        # Analyze baseline variability
        for test_type, data in baseline_results.items():
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
    
    def _generate_recommendations(self, baseline_results: Dict, mitigation_results: Dict) -> Dict:
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
                'implementation_notes': self.classifier.get_implementation_notes(flaky_type, best_strategy)
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
        
        return recommendations
    
    def update_cost_benefit_with_effectiveness(self, cost_benefit: Dict, effectiveness: Dict) -> Dict:
        """Update cost-benefit analysis with effectiveness data"""
        for strategy_name in cost_benefit.keys():
            if strategy_name in effectiveness:
                strategy_effectiveness = effectiveness[strategy_name]
                
                effectiveness_score = strategy_effectiveness.get('effectiveness_score', 0)
                improvement = strategy_effectiveness.get('pass_rate_improvement', {}).get('relative_percent', 0)
                overhead = strategy_effectiveness.get('performance_impact', {}).get('time_overhead_percent', 0)
                
                # Update costs with actual overhead
                cost_benefit[strategy_name]['costs']['performance_overhead'] = overhead / 10
                cost_benefit[strategy_name]['costs']['total'] = (
                    cost_benefit[strategy_name]['costs']['implementation'] +
                    cost_benefit[strategy_name]['costs']['maintenance'] +
                    overhead / 10
                )
                
                # Update benefits with actual improvement
                cost_benefit[strategy_name]['benefits']['improvement_score'] = improvement * 10
                cost_benefit[strategy_name]['benefits']['effectiveness_score'] = effectiveness_score
                
                # Recalculate ROI
                total_cost = cost_benefit[strategy_name]['costs']['total']
                benefit = improvement * 10
                roi = (benefit - total_cost) / total_cost if total_cost > 0 else 0
                cost_benefit[strategy_name]['roi'] = roi
                
                # Update recommendation
                cost_benefit[strategy_name]['recommendation'] = generate_strategy_recommendation(
                    strategy_name, roi, effectiveness_score)
        
        return cost_benefit
