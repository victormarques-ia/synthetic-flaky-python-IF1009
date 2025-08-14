"""
Report Generation Module
========================

Generates comprehensive reports and saves study data.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict
import pandas as pd


class ReportGenerator:
    """Generates comprehensive final reports and saves all data"""
    
    def __init__(self, study_start_time: float, study_metadata: Dict):
        self.study_start_time = study_start_time
        self.study_metadata = study_metadata
    
    def generate_report(self, analysis_results: Dict, baseline_results: Dict, 
                       mitigation_results: Dict, output_dir: Path):
        """Generate comprehensive final report"""
        print("📋 PHASE 4: REPORT GENERATION")
        print("=" * 50)
        
        # Generate text report
        report_content = self._generate_text_report(analysis_results, baseline_results, mitigation_results)
        
        # Save all data
        self._save_all_data(analysis_results, baseline_results, mitigation_results, output_dir)
        
        # Print final summary
        self._print_final_summary(analysis_results, output_dir)
        
        return report_content
    
    def _generate_text_report(self, analysis_results: Dict, baseline_results: Dict, 
                             mitigation_results: Dict) -> str:
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
        if analysis_results.get('cost_benefit_analysis'):
            best_strategy = max(analysis_results['cost_benefit_analysis'].items(),
                              key=lambda x: x[1]['roi'])
            
            total_experiments = (sum(data.get('total_runs', 0) for data in baseline_results.values()) + 
                               sum(data.get('total_runs', 0) for data in mitigation_results.values()))
            
            report_lines.extend([
                f"This study analyzed 5 types of flakiness and 4 mitigation strategies.",
                f"Best overall strategy: {best_strategy[0].upper()} (ROI: {best_strategy[1]['roi']:.2f})",
                f"Total experiments executed: {total_experiments}",
                ""
            ])
        
        # Flakiness classification
        if analysis_results.get('flakiness_classification'):
            report_lines.extend([
                "FLAKINESS CLASSIFICATION ANALYSIS",
                "-" * 40,
            ])
            
            for flaky_type, data in analysis_results['flakiness_classification'].items():
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
        if analysis_results.get('mitigation_effectiveness'):
            report_lines.extend([
                "MITIGATION STRATEGY EFFECTIVENESS",
                "-" * 40,
            ])
            
            for strategy, data in analysis_results['mitigation_effectiveness'].items():
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
        if analysis_results.get('cost_benefit_analysis'):
            report_lines.extend([
                "COST-BENEFIT ANALYSIS",
                "-" * 40,
            ])
            
            for strategy, data in analysis_results['cost_benefit_analysis'].items():
                roi = data['roi']
                recommendation = data['recommendation']
                
                report_lines.extend([
                    f"{strategy.upper()}:",
                    f"  • ROI: {roi:.2f}",
                    f"  • Recommendation: {recommendation}",
                    ""
                ])
        
        # Recommendations
        if analysis_results.get('recommendations'):
            recommendations = analysis_results['recommendations']
            
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
            f"  • Framework: {self.study_metadata.get('framework', 'synthetic_flaky_python')}",
            f"  • Study Type: {self.study_metadata.get('study_type', 'comprehensive_analysis')}",
            f"  • Timestamp: {self.study_metadata.get('timestamp', 'unknown')}",
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
        return report_content
    
    def _save_all_data(self, analysis_results: Dict, baseline_results: Dict, 
                      mitigation_results: Dict, output_dir: Path):
        """Save all experimental data and analysis results"""
        print("💾 Saving all data...")
        
        complete_data = {
            'study_metadata': self.study_metadata,
            'baseline_results': baseline_results,
            'mitigation_results': mitigation_results,
            'analysis_results': analysis_results,
            'study_duration_minutes': (time.time() - self.study_start_time) / 60
        }
        
        # Save complete data as JSON
        data_file = output_dir / "comprehensive_study_data.json"
        with open(data_file, 'w') as f:
            json.dump(complete_data, f, indent=2, default=str)
        
        # Save CSV summaries for easy analysis
        self._save_csv_summaries(baseline_results, mitigation_results, output_dir)
        
        # Save text report
        report_content = self._generate_text_report(analysis_results, baseline_results, mitigation_results)
        report_file = output_dir / "comprehensive_study_report.txt"
        with open(report_file, 'w') as f:
            f.write(report_content)
    
    def _save_csv_summaries(self, baseline_results: Dict, mitigation_results: Dict, output_dir: Path):
        """Save CSV summaries for easy analysis"""
        # Baseline summary
        if baseline_results:
            baseline_summary = []
            for test_type, data in baseline_results.items():
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
                output_dir / 'baseline_summary.csv', index=False)
        
        # Mitigation summary
        if mitigation_results:
            mitigation_summary = []
            for strategy, data in mitigation_results.items():
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
                output_dir / 'mitigation_summary.csv', index=False)
    
    def _print_final_summary(self, analysis_results: Dict, output_dir: Path):
        """Print final summary to console"""
        total_duration = (time.time() - self.study_start_time) / 60
        
        print("\n" + "=" * 70)
        print("🎉 COMPREHENSIVE STUDY COMPLETED!")
        print("=" * 70)
        print(f"📊 Study Duration: {total_duration:.1f} minutes")
        print(f"📁 Results Directory: {output_dir}")
        print()
        
        # Key findings summary
        if analysis_results.get('cost_benefit_analysis'):
            # Best strategy by ROI
            best_roi = max(analysis_results['cost_benefit_analysis'].items(),
                          key=lambda x: x[1]['roi'])
            
            # Most effective strategy
            if analysis_results.get('mitigation_effectiveness'):
                best_effectiveness = max(analysis_results['mitigation_effectiveness'].items(),
                                       key=lambda x: x[1]['effectiveness_score'])
                
                print("🏆 KEY FINDINGS:")
                print(f"   Best ROI: {best_roi[0].upper()} (ROI: {best_roi[1]['roi']:.2f})")
                print(f"   Most Effective: {best_effectiveness[0].upper()} (Score: {best_effectiveness[1]['effectiveness_score']:.3f})")
        
        # Flakiness insights
        if analysis_results.get('flakiness_classification'):
            most_problematic = min(analysis_results['flakiness_classification'].items(),
                                 key=lambda x: x[1]['observed_metrics']['avg_pass_rate'])
            
            print(f"   Most Problematic Type: {most_problematic[0].replace('_', ' ').title()} ({most_problematic[1]['observed_metrics']['avg_pass_rate']:.1%} pass rate)")
        
        print()
        print("📋 Generated Files:")
        print(f"   📄 comprehensive_study_report.txt - Complete analysis report")
        print(f"   📊 comprehensive_study_data.json - All raw data and results")
        print(f"   📈 *.png - Visualization charts (4 files)")
        print(f"   📝 *.csv - Summary tables (2 files)")
        print()
        print("✅ Study complete!")
    
    def update_implementation_priorities(self, analysis_results: Dict):
        """Update implementation priorities based on cost-benefit analysis"""
        if not analysis_results.get('cost_benefit_analysis'):
            return
        
        cost_benefit = analysis_results['cost_benefit_analysis']
        sorted_strategies = sorted(cost_benefit.items(), 
                                 key=lambda x: x[1]['roi'], reverse=True)
        
        priorities = [
            {
                'priority': i + 1,
                'strategy': strategy,
                'roi': data['roi'],
                'justification': data['recommendation']
            }
            for i, (strategy, data) in enumerate(sorted_strategies)
        ]
        
        if 'recommendations' not in analysis_results:
            analysis_results['recommendations'] = {}
        
        analysis_results['recommendations']['implementation_priorities'] = priorities
