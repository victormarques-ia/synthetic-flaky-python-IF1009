#!/usr/bin/env python3
"""
Simplified script to run flaky test experiments.
Executes the suite N times and saves results in JSON.

Configuration:
- Single suite: 50 tests (15 stable + 35 flaky)
- Rates: 0%, 5%, 10% (controlled by markers)
- Runs: 30 per configuration (total: 90 executions)
"""

import subprocess
import json
import sys
import time
from pathlib import Path
from datetime import datetime
import argparse


def setup_args():
    """Configure command line arguments"""
    parser = argparse.ArgumentParser(description="Run flaky test experiments")
    parser.add_argument("--runs", type=int, default=30, 
                       help="Number of runs per configuration (default: 30)")
    parser.add_argument("--output-dir", type=str, default="results",
                       help="Output directory (default: results)")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    return parser.parse_args()


def run_pytest_with_markers(markers, run_number, output_file, verbose=False):
    """Run pytest with specific markers"""
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--json-report",
        f"--json-report-file={output_file}",
        "-v" if verbose else "-q"
    ]
    
    # Adiciona filtros de markers se especificado
    if markers:
        cmd.extend(["-m", markers])
    
    if verbose:
        print(f"  Running: {' '.join(cmd)}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    # Adiciona metadados ao resultado
    if Path(output_file).exists():
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        data['experiment_meta'] = {
            'run_number': run_number,
            'markers': markers or "all",
            'duration_seconds': end_time - start_time,
            'timestamp': int(time.time()),
            'return_code': result.returncode,
            'command': ' '.join(cmd)
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    return result.returncode == 0


def main():
    """Main function"""
    args = setup_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print("🧪 SYNTHETIC FLAKY PYTHON - SIMPLIFIED EXPERIMENTS")
    print("=" * 55)
    print(f"Runs per configuration: {args.runs}")
    print(f"Output directory: {output_dir}")
    print(f"Total experiments: {args.runs * 3} (3 configurations)")
    print()
    
    # Experiment configurations
    # Simulate different flaky rates using marker subsets
    configurations = [
        {"name": "baseline_0pct", "markers": "stable", "description": "0% flaky (stable tests only)"},
        {"name": "mixed_5pct", "markers": "stable or randomness", "description": "~5% flaky (stable + randomness)"},
        {"name": "mixed_10pct", "markers": "stable or randomness or race", "description": "~10% flaky (stable + randomness + race)"}
    ]
    
    all_results = []
    total_start = time.time()
    
    for config in configurations:
        print(f"🔬 Running configuration: {config['name']}")
        print(f"   Description: {config['description']}")
        print(f"   Markers: {config['markers']}")
        
        config_results = []
        config_start = time.time()
        
        for run in range(1, args.runs + 1):
            output_file = output_dir / f"{config['name']}_run_{run:03d}.json"
            
            success = run_pytest_with_markers(
                config['markers'], 
                run, 
                str(output_file), 
                args.verbose
            )
            
            config_results.append({
                "run": run,
                "success": success,
                "output_file": str(output_file)
            })
            
            if not args.verbose and run % 10 == 0:
                successful = sum(1 for r in config_results if r['success'])
                print(f"   Progress: {run}/{args.runs} ({successful} successful)")
        
        config_end = time.time()
        config_duration = config_end - config_start
        successful_runs = sum(1 for r in config_results if r['success'])
        
        print(f"   ✅ Completed in {config_duration:.1f}s ({successful_runs}/{args.runs} successful)")
        print()
        
        all_results.append({
            "configuration": config,
            "duration": config_duration,
            "successful_runs": successful_runs,
            "total_runs": args.runs,
            "results": config_results
        })
    
    total_end = time.time()
    total_duration = total_end - total_start
    
    # Save experiment summary
    experiment_summary = {
        "experiment_info": {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "configurations_count": len(configurations),
            "runs_per_config": args.runs,
            "total_runs": len(configurations) * args.runs
        },
        "configurations": all_results
    }
    
    summary_file = output_dir / f"experiment_summary_{int(time.time())}.json"
    with open(summary_file, 'w') as f:
        json.dump(experiment_summary, f, indent=2)
    
    # Final statistics
    total_runs = sum(config['total_runs'] for config in all_results)
    total_successful = sum(config['successful_runs'] for config in all_results)
    
    print("=" * 55)
    print("📊 EXPERIMENT SUMMARY")
    print("=" * 55)
    print(f"Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"Total runs: {total_runs}")
    print(f"Successful runs: {total_successful}")
    print(f"Success rate: {total_successful/total_runs*100:.1f}%")
    print(f"Average time per run: {total_duration/total_runs:.2f}s")
    print()
    print(f"📁 Results saved in: {output_dir}/")
    print(f"📋 Summary: {summary_file}")
    print()
    print("🔍 Next steps:")
    print(f"   python scripts/analyze_results.py --input-dir {output_dir}")


if __name__ == "__main__":
    main()
