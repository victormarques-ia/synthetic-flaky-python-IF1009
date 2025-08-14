#!/usr/bin/env python3
"""
Comprehensive Flaky Test Study 
============================================

Unified orchestrator for complete empirical study of flaky test mitigation techniques.

Study Components:
1. Baseline Analysis - Execute tests without mitigation to establish flakiness patterns
2. Mitigation Analysis - Test 4 different mitigation strategies
3. Classification - Systematic analysis of 5 flakiness types
4. Effectiveness Metrics - Quantitative evaluation of each technique
5. Cost-Benefit Analysis - Performance overhead vs effectiveness
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

from config.study_config import StudyConfiguration
from classification.flakiness_classifier import FlakynessClassifier
from execution.experiment_runner import BaselineRunner, MitigationRunner
from analysis.data_analyzer import DataAnalyzer
from visualization.chart_generator import ChartGenerator
from reporting.report_generator import ReportGenerator
from utils.helpers import validate_output_directory


class ComprehensiveStudy:
    """Main orchestrator for executing the comprehensive flaky test study"""
    
    def __init__(self, config: StudyConfiguration):
        self.config = config
        self.output_dir = validate_output_directory(Path(config.output_dir))
        
        # Initialize components
        self.classifier = FlakynessClassifier()
        self.baseline_runner = BaselineRunner(config)
        self.mitigation_runner = MitigationRunner(config)
        self.analyzer = DataAnalyzer()
        self.chart_generator = ChartGenerator()
        
        # Study metadata
        self.study_start_time = time.time()
        self.study_metadata = {
            "study_type": "comprehensive_flaky_test_analysis",
            "framework": "synthetic_flaky_python",
            "timestamp": datetime.now().isoformat(),
            "configuration": config.__dict__
        }
        
        # Initialize report generator
        self.report_generator = ReportGenerator(self.study_start_time, self.study_metadata)
        
        # Results storage
        self.baseline_results = {}
        self.mitigation_results = {}
        self.analysis_results = {}
    
    def run_study(self) -> bool:
        """Execute the complete comprehensive study"""
        try:
            print("🧪 SYNTHETIC FLAKY PYTHON - COMPREHENSIVE STUDY")
            print("=" * 70)
            print("Empirical Study of Flaky Test Mitigation Techniques")
            print("Framework: Reproducible with fixed seeds")
            print("Comparison: 4 mitigation techniques across 5 flakiness types")
            print()
            
            self._print_configuration()
            
            # Phase 1: Baseline Analysis
            self.baseline_results = self.baseline_runner.run_experiments()
            
            # Phase 2: Mitigation Analysis
            self.mitigation_results = self.mitigation_runner.run_experiments()
            
            # Phase 3: Comprehensive Analysis
            self.analysis_results = self.analyzer.analyze(self.baseline_results, self.mitigation_results)
            
            # Update cost-benefit analysis with effectiveness data
            if ('mitigation_effectiveness' in self.analysis_results and 
                'cost_benefit_analysis' in self.analysis_results):
                self.analysis_results['cost_benefit_analysis'] = self.analyzer.update_cost_benefit_with_effectiveness(
                    self.analysis_results['cost_benefit_analysis'],
                    self.analysis_results['mitigation_effectiveness']
                )
            
            # Update implementation priorities
            self.report_generator.update_implementation_priorities(self.analysis_results)
            
            # Phase 4: Visualization and Reporting
            self.chart_generator.create_all_charts(
                self.analysis_results, 
                self.baseline_results, 
                self.mitigation_results, 
                self.output_dir
            )
            
            self.report_generator.generate_report(
                self.analysis_results,
                self.baseline_results,
                self.mitigation_results,
                self.output_dir
            )
            
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Study interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Error during study: {e}")
            if self.config.verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def _print_configuration(self):
        """Print study configuration"""
        print(f"Configuration:")
        print(f"  • Baseline runs per type: {self.config.baseline_runs}")
        print(f"  • Mitigation runs per strategy: {self.config.mitigation_runs}")
        print(f"  • Seeds: {self.config.seeds}")
        print(f"  • Output directory: {self.config.output_dir}")
        print(f"  • Skip baseline: {self.config.skip_baseline}")
        print(f"  • Skip mitigation: {self.config.skip_mitigation}")
        print()


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
    
    # Initialize and run study
    study = ComprehensiveStudy(config)
    success = study.run_study()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
