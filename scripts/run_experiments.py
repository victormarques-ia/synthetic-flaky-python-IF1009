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
import random
import numpy as np
import os
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
    parser.add_argument("--seeds", type=int, nargs='+', default=[42, 123, 999],
                       help="Random seeds for reproducibility (default: 42 123 999)")
    parser.add_argument("--single-seed", type=int, default=None,
                       help="Use single seed instead of multiple seeds")
    return parser.parse_args()


def set_random_seeds(seed):
    """Set random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    os.environ['RANDOM_SEED'] = str(seed)

# Em run_experiments.py, substitua a função inteira por esta:

def run_pytest_with_markers(markers, run_number, output_file, seed, verbose=False):
    """Run pytest with specific markers and seed, using an absolute path to tests."""
    if markers and "randomness" in markers:
        run_seed = (seed * 1000) + run_number
        set_random_seeds(run_seed)
    else:
        set_random_seeds(seed)
    
    # --- INÍCIO DA CORREÇÃO FINAL ---
    # Constrói o caminho absoluto para a pasta de testes
    # Isso garante que o pytest sempre encontre os arquivos corretos
    project_root = Path(__file__).parent.parent # Sobe dois níveis: scripts -> raiz do projeto
    tests_dir = project_root / "tests"
    # --- FIM DA CORREÇÃO FINAL ---
    
    cmd = [
        sys.executable, "-m", "pytest",
        str(tests_dir), # Usa o caminho absoluto
        "--json-report",
        f"--json-report-file={output_file}",
        "-v" if verbose else "-q"
    ]
    
    if markers:
        cmd.extend(["-m", markers])
    
    if verbose:
        print(f"  Running: {' '.join(cmd)}")
    
    env = os.environ.copy()
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    end_time = time.time()

    if result.returncode not in [0, 1, 5]: # Código 1 (falhas) agora é aceitável
        print(f"❌ ERRO FATAL no Pytest (run {run_number}, seed {seed}). Código: {result.returncode}", file=sys.stderr)
        if result.stdout:
            print("--- Stdout do Pytest: ---", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print("--- Stderr do Pytest: ---", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        return (0.0, 0, 0)
    
    if not Path(output_file).exists():
        if verbose:
            print(f"  ⚠️ Warning: No report file found for run {run_number}.", file=sys.stderr)
        return (0.0, 0, 0)

    try:
        with open(output_file, 'r+') as f:
            data = json.load(f)
            data['experiment_meta'] = {
                'run_number': run_number, 'markers': markers or "all", 'seed': seed,
                'effective_seed': run_seed if markers and "randomness" in markers else seed,
                'duration_seconds': end_time - start_time, 'timestamp': int(time.time()),
                'return_code': result.returncode, 'command': ' '.join(cmd)
            }
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

            summary = data.get('summary', {})
            passed = summary.get('passed', 0)
            total = summary.get('total', 0) 
            
            success_rate = passed / total if total > 0 else 0
            return (success_rate, passed, total)

    except (json.JSONDecodeError, IOError) as e:
        print(f"  ❌ Error processing JSON file {output_file}: {e}", file=sys.stderr)
        return (0.0, 0, 0)


def main():
    """Main function"""
    args = setup_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Determine seeds to use
    seeds = [args.single_seed] if args.single_seed is not None else args.seeds
    
    print("🧪 SYNTHETIC FLAKY PYTHON - SIMPLIFIED EXPERIMENTS")
    print("=" * 55)
    print(f"Runs per configuration: {args.runs}")
    print(f"Seeds used: {seeds}")
    print(f"Output directory: {output_dir}")
    print(f"Total experiments: {args.runs * len(seeds) * 3} (3 configurations × {len(seeds)} seeds)")
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
        
        for seed in seeds:
            print(f"   🌱 Using seed: {seed}")
            for run in range(1, args.runs + 1):
                output_file = output_dir / f"{config['name']}_seed_{seed}_run_{run:03d}.json"
                
                success_rate, passed_tests, total_tests = run_pytest_with_markers(
                    config['markers'], 
                    run, 
                    str(output_file), 
                    seed,
                    args.verbose
                )
            
                config_results.append({
                    "seed": seed,
                    "run": run,
                    "success_rate": success_rate,
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                    "output_file": str(output_file)
                })
                
                if not args.verbose and run % 10 == 0:
                    total_tests_passed = sum(r.get('passed_tests', 0) for r in config_results)
                    total_possible = sum(r.get('total_tests', 0) for r in config_results)
                    current_rate = (total_tests_passed / total_possible * 100) if total_possible > 0 else 0
                    print(f"   Progress: seed {seed}, run {run}/{args.runs} ({current_rate:.1f}% tests passing)")
        
        config_end = time.time()
        config_duration = config_end - config_start
        
        # Calculate real success statistics
        total_tests_passed = sum(r.get('passed_tests', 0) for r in config_results)
        total_possible_tests = sum(r.get('total_tests', 0) for r in config_results)
        overall_success_rate = (total_tests_passed / total_possible_tests * 100) if total_possible_tests > 0 else 0
        
        print(f"   ✅ Completed in {config_duration:.1f}s ({overall_success_rate:.1f}% tests passed)")
        print()
        
        all_results.append({
            "configuration": config,
            "duration": config_duration,
            "tests_passed": total_tests_passed,
            "total_possible_tests": total_possible_tests,
            "success_rate_percent": overall_success_rate,
            "total_runs": args.runs * len(seeds),  # Fixed: account for all seeds
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
        "seeds_used": seeds,
        "total_runs": len(configurations) * args.runs * len(seeds)
        },
        "configurations": all_results
    }
    
    summary_file = output_dir / f"experiment_summary_{int(time.time())}.json"
    with open(summary_file, 'w') as f:
        json.dump(experiment_summary, f, indent=2)
    
    # Final statistics
    total_runs = sum(config['total_runs'] for config in all_results)
    total_tests_passed = sum(config['tests_passed'] for config in all_results)
    total_possible_tests = sum(config['total_possible_tests'] for config in all_results)
    overall_success_rate = (total_tests_passed / total_possible_tests * 100) if total_possible_tests > 0 else 0
    
    print("=" * 55)
    print("📊 EXPERIMENT SUMMARY")
    print("=" * 55)
    print(f"Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"Total runs: {total_runs}")
    print(f"Tests passed: {total_tests_passed}/{total_possible_tests}")
    print(f"Overall success rate: {overall_success_rate:.1f}%")
    print(f"Average time per run: {total_duration/total_runs:.2f}s")
    print()
    print("📊 Configuration Results:")
    for config in all_results:
        name = config['configuration']['name']
        rate = config['success_rate_percent']
        flaky_rate = 100 - rate
        print(f"   {name}: {rate:.1f}% pass rate ({flaky_rate:.1f}% flaky)")
    print()
    print(f"📁 Results saved in: {output_dir}/")
    print(f"📋 Summary: {summary_file}")
    print()
    print("🔍 Next steps:")
    print(f"   python scripts/analyze_results.py --input-dir {output_dir}")


if __name__ == "__main__":
    main()
