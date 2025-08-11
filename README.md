# Synthetic Flaky Python

A **simple and focused** framework for studying flaky (unstable) tests in Python, developed for academic projects.

## 📋 Overview

This project implements a controlled benchmark to study different types of flakiness in automated tests. The framework allows:

- **Run experiments** with 56 tests (15 stable + 41 flaky)
- **Analyze instability** with statistical metrics
- **Visualize results** with automatic graphs
- **Compare configurations** (0%, ~5%, ~10% flakiness)

## 🏗️ Project Structure

```
synthetic-flaky-python/
├── tests/                          # Fixed test suite
│   ├── test_stable.py              # 15 tests always pass
│   ├── test_flaky_randomness.py    # 10 random tests  
│   ├── test_flaky_race.py          # 8 race condition tests
│   ├── test_flaky_order.py         # 13 order dependency tests
│   ├── test_flaky_external.py      # 10 external dependency tests
│   ├── test_flaky_timeout.py       # 10 timeout tests
│   └── pytest.ini                  # pytest configuration
├── scripts/
│   ├── run_experiments.py          # Run experiments
│   └── analyze_results.py          # Analyze results
├── results/                        # Experiment results
└── README.md
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd synthetic-flaky-python

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Experiments

```bash
# Complete experiment (30 runs × 3 configurations = 90 executions)
python scripts/run_experiments.py --runs 30

# Quick test experiment (3 runs × 3 configurations = 9 executions)
python scripts/run_experiments.py --runs 3 --verbose
```

### 3. Analyze Results

```bash
# Complete analysis with visualizations
python scripts/analyze_results.py --verbose

# Results saved in results/
```

## 🧪 Types of Flaky Tests

The framework implements **5 main categories** of flakiness:

### 1. **Randomness** (10 tests)
Tests that depend on random numbers or probability.

**Example:**
```python
def test_random_coin_flip():
    """Fails ~50% of the time"""
    assert random.random() > 0.5
```

### 2. **Race Conditions** (8 tests)
Race conditions between threads and concurrency issues.

**Example:**
```python
def test_race_counter_increment():
    """Race condition in shared counter"""
    # Two threads incrementing simultaneously
    assert shared_counter["value"] == 20  # May fail
```

### 3. **Order Dependencies** (13 tests)
Tests that depend on execution order or global state.

**Example:**
```python
def test_order_use_state():
    """Depends on test_order_initialize running first"""
    assert global_state["initialized"] is True
```

### 4. **External Dependencies** (10 tests)
Simulation of unstable APIs, databases, and external services.

**Example:**
```python
def test_external_api_call():
    """Simulates API that may fail (30% chance)"""
    response = MockExternalAPI.get_user_data(123)
    assert response["id"] == 123
```

### 5. **Timeout Issues** (10 tests)
Tests sensitive to performance and time limitations.

**Example:**
```python
def test_timeout_deadline_sensitive():
    """Fails if processing takes too long"""
    duration = measure_processing_time()
    assert duration < 0.02  # 20ms limit
```

## 📊 Experiment Configurations

The framework tests **3 different configurations**:

| Configuration | Description | Tests Included |
|--------------|-------------|----------------|
| **baseline_0pct** | 0% flaky (control) | Only `test_stable.py` (15 tests) |
| **mixed_5pct** | ~5% flaky | `stable` + `randomness` (25 tests) |
| **mixed_10pct** | ~10% flaky | `stable` + `randomness` + `race` (33 tests) |

## 📈 Collected Metrics

### **Core Metrics**
- **Pass Rate**: proportion of successful executions
- **Flakiness Rate**: % of tests showing flaky behavior  
- **Instability Index**: number of pass↔fail transitions per test
- **Execution Time**: average execution time

### **Generated Analysis**
- **CSV**: `flakiness_analysis.csv`, `run_metadata.csv`
- **JSON**: `summary_statistics.json`
- **Graphs**: `flakiness_analysis.png`, `pass_rate_distribution.png`

## 📋 Example Results

```
📊 FLAKINESS ANALYSIS - SUMMARY
============================================================

🔬 Configuration: baseline_0pct
   Total tests: 15
   Flaky tests: 0 (0.0%)
   Average pass rate: 1.000

🔬 Configuration: mixed_5pct  
   Total tests: 25
   Flaky tests: 5 (20.0%)
   Average pass rate: 0.787

🔬 Configuration: mixed_10pct
   Total tests: 33
   Flaky tests: 8 (24.2%)
   Average pass rate: 0.802

🔴 TOP 5 MOST UNSTABLE TESTS:
   1. test_race_flag_timing (instability: 2, pass rate: 0.67)
   2. test_random_coin_flip (instability: 2, pass rate: 0.33)
   3. test_random_low_probability (instability: 2, pass rate: 0.33)
```

## ⚙️ Configuration Options

### Experiment Script (`run_experiments.py`)

```bash
python scripts/run_experiments.py [options]

Options:
  --runs N              Number of runs per configuration (default: 30)
  --output-dir DIR      Output directory (default: results)
  --verbose            Detailed output
```

### Analysis Script (`analyze_results.py`)

```bash
python scripts/analyze_results.py [options]

Options:
  --input-dir DIR       Directory with results (default: results)
  --output-dir DIR      Output directory (default: results)
  --verbose            Detailed output
```

## 🎓 For Academic Projects

### **Recommended Configuration**
```bash
# Standard experiment for thesis/dissertation
python scripts/run_experiments.py --runs 30  # 90 total executions
python scripts/analyze_results.py --verbose   # Complete analysis
```

### **Execution Time**
- **Complete experiment**: ~5-8 minutes
- **Analysis**: ~30 seconds
- **Total**: less than 10 minutes

### **Data for Report**
- Ready-to-use tables in CSV
- High-resolution graphs (PNG)
- Structured statistics in JSON
- Ranking of most unstable tests

## 🔬 Customization

### **Adding New Tests**
1. Edit files in `tests/test_flaky_*.py`
2. Use appropriate markers: `@pytest.mark.flaky`, `@pytest.mark.randomness`
3. Run experiments again

### **Modifying Configurations**
Edit configurations in `scripts/run_experiments.py`:

```python
configurations = [
    {"name": "baseline_0pct", "markers": "stable"},
    {"name": "custom_config", "markers": "stable or timeout"},
    # Add your configurations
]
```

## 📚 Data Structure

### Result File (`*.json`)
```json
{
  "summary": {
    "collected": 25,
    "passed": 20,
    "failed": 5
  },
  "tests": [
    {
      "nodeid": "tests/test_stable.py::test_stable_arithmetic",
      "outcome": "passed",
      "duration": 0.001
    }
  ],
  "experiment_meta": {
    "run_number": 1,
    "markers": "stable or randomness",
    "duration_seconds": 0.51
  }
}
```

### Flakiness Analysis (`flakiness_analysis.csv`)
```csv
configuration,test_name,total_runs,passes,fails,pass_rate,is_flaky,instability_index
baseline_0pct,test_stable_arithmetic,30,30,0,1.0,False,0
mixed_5pct,test_random_coin_flip,30,15,15,0.5,True,8
```

## 🤝 Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/new-flaky-type`)
3. Commit changes (`git commit -am 'Add timeout flaky'`)
4. Push to branch (`git push origin feature/new-flaky-type`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🎯 Next Steps

1. **Run the experiment**: `python scripts/run_experiments.py --runs 30`
2. **Analyze results**: `python scripts/analyze_results.py`
3. **Use the data**: CSV tables and PNG graphs for your report
4. **Customize**: Add new types of flakiness as needed

---

**Synthetic Flaky Python** - Simple framework for research in automated test flakiness 🧪