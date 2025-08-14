"""
Chart Generation Module
=======================

Creates comprehensive visualizations for the flaky test study results.
"""

from pathlib import Path
from typing import Dict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from classification.flakiness_classifier import FlakynessClassifier


class ChartGenerator:
    """Generates publication-quality visualizations"""
    
    def __init__(self):
        self.classifier = FlakynessClassifier()
        self.flakiness_profiles = self.classifier.get_flakiness_profiles()
    
    def create_all_charts(self, analysis_results: Dict, baseline_results: Dict, 
                         mitigation_results: Dict, output_dir: Path):
        """Create all visualizations for the study"""
        print("📊 Creating visualizations...")
        
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Flakiness Classification Overview
        self._create_flakiness_overview_plot(analysis_results, output_dir)
        
        # 2. Mitigation Effectiveness Comparison
        self._create_mitigation_effectiveness_plot(analysis_results, output_dir)
        
        # 3. Cost-Benefit Analysis
        self._create_cost_benefit_plot(analysis_results, output_dir)
        
        # 4. Detailed Performance Analysis
        self._create_performance_analysis_plot(baseline_results, mitigation_results, output_dir)
    
    def _create_flakiness_overview_plot(self, analysis_results: Dict, output_dir: Path):
        """Create flakiness classification overview plot"""
        flakiness_data = analysis_results.get('flakiness_classification', {})
        if not flakiness_data:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Flakiness Classification Analysis', fontsize=16, fontweight='bold')
        
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
        plt.savefig(output_dir / 'flakiness_classification.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_mitigation_effectiveness_plot(self, analysis_results: Dict, output_dir: Path):
        """Create mitigation effectiveness comparison plot"""
        effectiveness_data = analysis_results.get('mitigation_effectiveness', {})
        if not effectiveness_data:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Mitigation Strategy Effectiveness Analysis', fontsize=16, fontweight='bold')
        
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
        plt.savefig(output_dir / 'mitigation_effectiveness.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_cost_benefit_plot(self, analysis_results: Dict, output_dir: Path):
        """Create cost-benefit analysis plot"""
        cost_benefit_data = analysis_results.get('cost_benefit_analysis', {})
        if not cost_benefit_data:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Cost-Benefit Analysis', fontsize=16, fontweight='bold')
        
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
        plt.savefig(output_dir / 'cost_benefit_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_performance_analysis_plot(self, baseline_results: Dict, mitigation_results: Dict, output_dir: Path):
        """Create detailed performance analysis plot"""
        if not baseline_results or not mitigation_results:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Detailed Performance Analysis', fontsize=16, fontweight='bold')
        
        # Baseline performance by flakiness type
        baseline_types = []
        baseline_pass_rates = []
        baseline_exec_times = []
        
        for test_type, data in baseline_results.items():
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
        if mitigation_results:
            mit_strategies = list(mitigation_results.keys())
            mit_pass_rates = [data['avg_pass_rate'] for data in mitigation_results.values()]
            mit_exec_times = [data['avg_execution_time'] for data in mitigation_results.values()]
            
            # Add baseline for comparison
            baseline_flaky = baseline_results.get('all_flaky', {})
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
        plt.savefig(output_dir / 'performance_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
