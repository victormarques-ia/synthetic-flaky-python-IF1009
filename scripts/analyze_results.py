#!/usr/bin/env python3
"""
Simplified script to analyze flaky test experiment results.
Processes JSON files and generates basic metrics and visualizations.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from pathlib import Path
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)


def setup_args():
    """Configure command line arguments"""
    parser = argparse.ArgumentParser(description="Analyze flaky test results")
    parser.add_argument("--input-dir", type=str, default="results",
                       help="Input directory with JSON files (default: results)")
    parser.add_argument("--output-dir", type=str, default="results",
                       help="Output directory for analysis (default: results)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    return parser.parse_args()


def load_experiment_data(input_dir, verbose=False):
    """Load data from all JSON files"""
    input_path = Path(input_dir)
    json_files = list(input_path.glob("*_run_*.json"))
    
    if not json_files:
        raise FileNotFoundError(f"No result files found in {input_path}")
    
    if verbose:
        print(f"Found {len(json_files)} result files")
    
    test_records = []
    run_metadata = []
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Extrai metadados do run
            meta = data.get('experiment_meta', {})
            config_name = json_file.stem.split('_run_')[0]  # baseline_0pct, mixed_5pct, etc.
            
            run_info = {
                'configuration': config_name,
                'run_number': meta.get('run_number', 0),
                'duration': meta.get('duration_seconds', 0),
                'markers': meta.get('markers', 'unknown'),
                'tests_collected': data.get('summary', {}).get('collected', 0),
                'tests_passed': data.get('summary', {}).get('passed', 0),
                'tests_failed': data.get('summary', {}).get('failed', 0),
                'tests_skipped': data.get('summary', {}).get('skipped', 0)
            }
            run_metadata.append(run_info)
            
            # Extrai dados de cada teste
            for test in data.get('tests', []):
                record = {
                    'configuration': config_name,
                    'run_number': meta.get('run_number', 0),
                    'test_name': test.get('nodeid', '').split('::')[-1],
                    'test_file': test.get('nodeid', '').split('::')[0].replace('tests/', ''),
                    'outcome': test.get('outcome', 'unknown'),
                    'duration': test.get('duration', 0),
                    'markers': test.get('keywords', [])
                }
                test_records.append(record)
                
        except Exception as e:
            if verbose:
                print(f"Warning: Failed to process {json_file}: {e}")
    
    return pd.DataFrame(test_records), pd.DataFrame(run_metadata)


def analyze_flakiness(test_df, verbose=False):
    """Analyze flakiness patterns"""
    if verbose:
        print("Analyzing flakiness patterns...")
    
    # Group by configuration and test
    flakiness_analysis = []
    
    for config in test_df['configuration'].unique():
        config_data = test_df[test_df['configuration'] == config]
        
        for test_name in config_data['test_name'].unique():
            test_data = config_data[config_data['test_name'] == test_name]
            
            total_runs = len(test_data)
            passes = (test_data['outcome'] == 'passed').sum()
            fails = (test_data['outcome'] == 'failed').sum()
            
            # Calcula instability index (transições pass/fail)
            outcomes = test_data.sort_values('run_number')['outcome'].tolist()
            transitions = sum(1 for i in range(1, len(outcomes)) 
                            if outcomes[i] != outcomes[i-1])
            
            flakiness_analysis.append({
                'configuration': config,
                'test_name': test_name,
                'test_file': test_data['test_file'].iloc[0],
                'total_runs': total_runs,
                'passes': passes,
                'fails': fails,
                'pass_rate': passes / total_runs if total_runs > 0 else 0,
                'is_flaky': (passes > 0) and (fails > 0),
                'instability_index': transitions,
                'avg_duration': test_data['duration'].mean()
            })
    
    return pd.DataFrame(flakiness_analysis)


def generate_summary_stats(flaky_df, run_df, verbose=False):
    """Generate summary statistics"""
    if verbose:
        print("Generating summary statistics...")
    
    summary = {}
    
    for config in flaky_df['configuration'].unique():
        config_data = flaky_df[flaky_df['configuration'] == config]
        config_runs = run_df[run_df['configuration'] == config]
        
        total_tests = len(config_data)
        flaky_tests = config_data['is_flaky'].sum()
        
        summary[config] = {
            'total_tests': total_tests,
            'flaky_tests': int(flaky_tests),
            'flaky_percentage': (flaky_tests / total_tests * 100) if total_tests > 0 else 0,
            'avg_pass_rate': config_data['pass_rate'].mean(),
            'avg_instability': config_data['instability_index'].mean(),
            'avg_duration_per_run': config_runs['duration'].mean(),
            'total_runs': len(config_runs)
        }
    
    return summary


def create_visualizations(flaky_df, run_df, output_dir):
    """Create visualizations of results"""
    plt.style.use('default')
    sns.set_palette("husl")
    
    output_path = Path(output_dir)
    
    # 1. Flakiness por configuração
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Number of flaky tests per configuration
    flaky_by_config = flaky_df.groupby('configuration')['is_flaky'].sum()
    axes[0,0].bar(flaky_by_config.index, flaky_by_config.values)
    axes[0,0].set_title('Number of Flaky Tests per Configuration')
    axes[0,0].set_ylabel('Flaky Tests')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Add values on bars
    for i, v in enumerate(flaky_by_config.values):
        axes[0,0].text(i, v + 0.1, str(int(v)), ha='center')
    
    # Average pass rate per configuration
    pass_rate_by_config = flaky_df.groupby('configuration')['pass_rate'].mean()
    axes[0,1].bar(pass_rate_by_config.index, pass_rate_by_config.values)
    axes[0,1].set_title('Average Pass Rate per Configuration')
    axes[0,1].set_ylabel('Pass Rate')
    axes[0,1].set_ylim(0, 1)
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # Run duration per configuration
    axes[1,0].boxplot([run_df[run_df['configuration'] == config]['duration'] 
                      for config in run_df['configuration'].unique()],
                     labels=run_df['configuration'].unique())
    axes[1,0].set_title('Run Duration Distribution')
    axes[1,0].set_ylabel('Duration (seconds)')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # Instability index for flaky tests
    flaky_only = flaky_df[flaky_df['is_flaky']]
    if not flaky_only.empty:
        for config in flaky_only['configuration'].unique():
            config_flaky = flaky_only[flaky_only['configuration'] == config]
            axes[1,1].scatter(config_flaky['pass_rate'], config_flaky['instability_index'], 
                            label=config, alpha=0.7)
        
        axes[1,1].set_xlabel('Pass Rate')
        axes[1,1].set_ylabel('Instability Index')
        axes[1,1].set_title('Instability vs Pass Rate (Testes Flaky)')
        axes[1,1].legend()
    
    plt.tight_layout()
    plt.savefig(output_path / 'flakiness_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Distribuição de pass rates
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for config in flaky_df['configuration'].unique():
        config_data = flaky_df[flaky_df['configuration'] == config]
        ax.hist(config_data['pass_rate'], bins=10, alpha=0.6, label=config)
    
    ax.set_xlabel('Pass Rate')
    ax.set_ylabel('Frequência')
    ax.set_title('Distribuição de Pass Rates por Configuração')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_path / 'pass_rate_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()


def save_results(flaky_df, run_df, summary_stats, output_dir):
    """Save results to files"""
    output_path = Path(output_dir)
    
    # CSV with flakiness analysis
    flaky_df.to_csv(output_path / 'flakiness_analysis.csv', index=False)
    
    # CSV with run metadata
    run_df.to_csv(output_path / 'run_metadata.csv', index=False)
    
    # JSON with summary statistics
    with open(output_path / 'summary_statistics.json', 'w') as f:
        json.dump(summary_stats, f, indent=2)


def print_summary_report(summary_stats, flaky_df):
    """Print summary report to console"""
    print("\n" + "="*60)
    print("📊 FLAKINESS ANALYSIS - SUMMARY")
    print("="*60)
    
    for config, stats in summary_stats.items():
        print(f"\n🔬 Configuration: {config}")
        print(f"   Total tests: {stats['total_tests']}")
        print(f"   Flaky tests: {stats['flaky_tests']} ({stats['flaky_percentage']:.1f}%)")
        print(f"   Average pass rate: {stats['avg_pass_rate']:.3f}")
        print(f"   Average instability: {stats['avg_instability']:.2f}")
        print(f"   Average duration per run: {stats['avg_duration_per_run']:.2f}s")
        print(f"   Total runs: {stats['total_runs']}")
    
    # Top 5 most unstable tests
    top_flaky = flaky_df[flaky_df['is_flaky']].nlargest(5, 'instability_index')
    if not top_flaky.empty:
        print(f"\n🔴 TOP 5 MOST UNSTABLE TESTS:")
        for idx, (_, test) in enumerate(top_flaky.iterrows(), 1):
            print(f"   {idx}. {test['test_name']} (instability: {test['instability_index']}, pass rate: {test['pass_rate']:.2f})")


def main():
    """Main function"""
    args = setup_args()
    
    print("📊 SYNTHETIC FLAKY PYTHON - RESULTS ANALYSIS")
    print("=" * 50)
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print()
    
    try:
        # Load data
        test_df, run_df = load_experiment_data(args.input_dir, args.verbose)
        print(f"Loaded {len(test_df)} test records from {len(run_df)} runs")
        
        # Analyze flakiness
        flaky_df = analyze_flakiness(test_df, args.verbose)
        
        # Generate statistics
        summary_stats = generate_summary_stats(flaky_df, run_df, args.verbose)
        
        # Create visualizations
        print("Generating visualizations...")
        create_visualizations(flaky_df, run_df, args.output_dir)
        
        # Save results
        print("Saving results...")
        save_results(flaky_df, run_df, summary_stats, args.output_dir)
        
        # Print report
        print_summary_report(summary_stats, flaky_df)
        
        print(f"\n✅ Analysis completed! Results saved in: {args.output_dir}")
        print(f"📊 Visualizations: flakiness_analysis.png, pass_rate_distribution.png")
        print(f"📋 Data: flakiness_analysis.csv, run_metadata.csv")
        print(f"📈 Summary: summary_statistics.json")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
