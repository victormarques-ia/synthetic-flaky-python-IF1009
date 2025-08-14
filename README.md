# Synthetic Flaky Python

A **comprehensive framework** for empirical study of flaky test mitigation techniques, developed for academic research.

## 📋 Overview

This project implements a controlled benchmark to study different types of flakiness and mitigation strategies in automated tests. The framework provides:

- **Systematic Classification** of 5 main flakiness types with controlled reproduction
- **Empirical Evaluation** of 4 mitigation techniques with quantitative metrics  
- **Cost-Benefit Analysis** of each technique with ROI calculations
- **Practical Recommendations** for developers based on data-driven insights
- **Reproducible Framework** with fixed seeds for consistent results

## 🏗️ Project Structure

```
synthetic-flaky-python/
├── tests/                          # Comprehensive test suite (5 flakiness types)
│   ├── test_stable.py              # stable tests (baseline)
│   ├── test_flaky_randomness.py    # randomness-based flaky tests  
│   ├── test_flaky_race.py          # race condition tests
│   ├── test_flaky_order.py         # order dependency tests
│   ├── test_flaky_external.py      # external dependency tests
│   ├── test_flaky_timeout.py       # timeout-sensitive tests
│   └── pytest.ini                  # pytest configuration
├── scripts/
│   ├── run_comprehensive_study.py  # 🆕 MAIN: orchestrator script
│   ├── config/                     # Configuration management
│   │   └── study_config.py         # Study settings and flakiness profiles
│   ├── classification/             # Flakiness classification system
│   │   └── flakiness_classifier.py # Systematic type classification
│   ├── execution/                  # Test execution engines
│   │   └── experiment_runner.py    # Baseline and mitigation runners
│   ├── analysis/                   # Data analysis modules
│   │   └── data_analyzer.py        # Statistical analysis and metrics
│   ├── visualization/              # Chart generation
│   │   └── chart_generator.py      # Publication-quality visualizations
│   ├── reporting/                  # Report generation
│   │   └── report_generator.py     # Text reports and data persistence
│   ├── utils/                      # Shared utilities
│   │   └── helpers.py              # Common helper functions
│   ├── MODULE_STRUCTURE.md         # 📋 Detailed module documentation
├── comprehensive_results/          # Complete study results
└── README.md
```

## 🏛️ Modular Architecture

The framework uses a **modular design** for maintainability and extensibility:

- **🎯 `run_comprehensive_study.py`**: Main orchestrator script
- **⚙️ `config/`**: Centralized configuration and flakiness type definitions
- **🔬 `classification/`**: Systematic flakiness classification system  
- **⚡ `execution/`**: Test execution engines for baseline and mitigation
- **📊 `analysis/`**: Statistical analysis and effectiveness metrics
- **📈 `visualization/`**: Publication-quality chart generation
- **📋 `reporting/`**: Report generation and data persistence
- **🛠️ `utils/`**: Shared helper functions and utilities

📋 **Detailed Architecture**: See [`scripts/MODULE_STRUCTURE.md`](scripts/MODULE_STRUCTURE.md) for complete module documentation.

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd synthetic-flaky-python

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (includes mitigation packages)
pip install -r requirements.txt
```

### 2. Run Complete Study

```bash
# 🎯 COMPREHENSIVE STUDY (RECOMMENDED)
# Executes baseline analysis + mitigation strategies + complete analysis
python scripts/run_comprehensive_study.py

# Quick test (for development/testing)
python scripts/run_comprehensive_study.py --baseline-runs 2 --mitigation-runs 2

# With custom settings
python scripts/run_comprehensive_study.py --baseline-runs 10 --mitigation-runs 10 --verbose
```

### 3. Results Generated

```bash
# All results saved in comprehensive_results/
# ✅ comprehensive_study_report.txt     - Complete analysis report
# ✅ comprehensive_study_data.json      - All raw data and results  
# ✅ *.png                              - 4 visualization charts
# ✅ *.csv                              - Summary tables for analysis
```

## 🧪 Flakiness Classification System

The framework systematically implements **5 main categories** of flakiness for empirical analysis:

### 1. **Randomness**
Tests that depend on random numbers or probability.

**Example:**
```python
def test_random_coin_flip():
    """Fails ~50% of the time"""
    assert random.random() > 0.5
```

### 2. **Race Conditions**
Race conditions between threads and concurrency issues.

**Example:**
```python
def test_race_counter_increment():
    """Race condition in shared counter"""
    # Two threads incrementing simultaneously
    assert shared_counter["value"] == 20  # May fail
```

### 3. **Order Dependencies**
Tests that depend on execution order or global state.

**Example:**
```python
def test_order_use_state():
    """Depends on test_order_initialize running first"""
    assert global_state["initialized"] is True
```

### 4. **External Dependencies** 
Simulation of unstable APIs, databases, and external services.

**Example:**
```python
def test_external_api_call():
    """Simulates API that may fail (30% chance)"""
    response = MockExternalAPI.get_user_data(123)
    assert response["id"] == 123
```

### 5. **Timeout Issues**
Tests sensitive to performance and time limitations.

**Example:**
```python
def test_timeout_deadline_sensitive():
    """Fails if processing takes too long"""
    duration = measure_processing_time()
    assert duration < 0.02  # 20ms limit
```

## 🛠️ Mitigation Strategies

The framework evaluates **4 main mitigation techniques**:

### 1. **Retries** (pytest-rerunfailures)
Re-execute failed tests multiple times to handle transient failures.

**Configuration:**
```bash
pytest --reruns=3 --reruns-delay=1
```

**Best for:** Timeout issues, external dependencies
**Pros:** Easy to implement, low maintenance
**Cons:** Increases execution time, doesn't fix root cause

### 2. **Mocking** (unittest.mock)
Replace unreliable dependencies with predictable mock objects.

**Example:**
```python
@patch('random.random')
def test_with_mock(mock_random):
    mock_random.return_value = 0.8  # Deterministic
    assert random.random() > 0.5    # Always passes
```

**Best for:** External dependencies, randomness
**Pros:** Eliminates external failures, fast execution
**Cons:** High maintenance, may miss integration issues

### 3. **Test Isolation** (pytest-forked)
Execute each test in a separate process to prevent state sharing.

**Configuration:**
```bash
pytest --forked
```

**Best for:** Order dependencies, race conditions
**Pros:** Prevents state contamination, reliable
**Cons:** Slower execution, higher resource usage

### 4. **Combined Strategy**
Use multiple techniques together for maximum effectiveness.

**Configuration:**
```bash
pytest --reruns=2 --forked  # + mocking
```

**Best for:** Complex systems with multiple flakiness types
**Pros:** Highest effectiveness
**Cons:** Most complex and expensive to implement

## 📊 Comprehensive Study Design

The framework executes a **two-phase empirical study**:

### **Phase 1: Baseline Analysis**
Tests each flakiness type separately to establish baseline characteristics:

### **Phase 2: Mitigation Analysis**
Tests each mitigation strategy against all flaky tests to measure effectiveness.

## 📈 Comprehensive Metrics

### **Flakiness Classification Metrics**
- **Pass Rate**: Proportion of successful test executions
- **Flakiness Index**: Coefficient of variation in pass rates (instability measure)
- **Severity Classification**: Low/Moderate/High/Severe based on index
- **Predictability**: Consistency of failure patterns

### **Mitigation Effectiveness Metrics**
- **Improvement Rate**: Relative % improvement in pass rates
- **Performance Overhead**: % increase in execution time
- **Effectiveness Score**: Weighted score considering improvement vs overhead
- **Cost-Effectiveness Ratio**: Improvement per unit of overhead

### **Cost-Benefit Analysis**
- **Implementation Cost**: Relative complexity to implement (1-10 scale)
- **Maintenance Cost**: Ongoing effort required (1-10 scale)
- **Return on Investment (ROI)**: (Benefits - Costs) / Costs
- **Strategy Ranking**: Ordered by ROI and effectiveness

### **Generated Outputs**
- **📄 comprehensive_study_report.txt**: Complete analysis with recommendations
- **📊 comprehensive_study_data.json**: All raw data and calculated metrics
- **📈 Visualizations**: 4 charts covering all aspects of the study
- **📋 CSV Summaries**: Baseline and mitigation data for further analysis

## 📋 Example Study Results

```
🎉 COMPREHENSIVE STUDY COMPLETED!
======================================================================
📊 Study Duration: 12.3 minutes
📁 Results Directory: comprehensive_results/

🏆 KEY FINDINGS:
   Best ROI: RETRIES (ROI: 2.45)
   Most Effective: COMBINED (Score: 0.847)
   Most Problematic Type: Randomness (47.2% pass rate)

FLAKINESS CLASSIFICATION ANALYSIS
----------------------------------------
RANDOMNESS:
  • Pass Rate: 47.2% (flakiness index: 0.342)
  • Severity: High
  • Mechanism: Non-deterministic assertions based on random values

EXTERNAL:
  • Pass Rate: 68.5% (flakiness index: 0.198)
  • Severity: Moderate  
  • Mechanism: Network failures and service unavailability

MITIGATION STRATEGY EFFECTIVENESS
----------------------------------------
RETRIES:
  • Pass Rate Improvement: +23.4%
  • Performance Overhead: +47.2%
  • Effectiveness Score: 0.634

MOCKING:
  • Pass Rate Improvement: +41.8%
  • Performance Overhead: +12.1%
  • Effectiveness Score: 0.798

PRACTICAL RECOMMENDATIONS
----------------------------------------
Implementation Priority Ranking:
  1. MOCKING (ROI: 3.12)
  2. RETRIES (ROI: 2.45)
  3. ISOLATION (ROI: 1.89)
  4. COMBINED (ROI: 1.34)

Recommendations by Flakiness Type:
  • Randomness: Use MOCKING (Expected effectiveness: 90%)
  • External: Use MOCKING (Expected effectiveness: 95%)
  • Race: Use ISOLATION (Expected effectiveness: 90%)
```

## ⚙️ Configuration Options

### Comprehensive Study Script (`run_comprehensive_study.py`)

```bash
python scripts/run_comprehensive_study.py [options]

Options:
  --baseline-runs N     Runs per baseline type (default: 15)
  --mitigation-runs N   Runs per mitigation strategy (default: 15)  
  --output-dir DIR      Output directory (default: comprehensive_results)
  --seeds N N N         Random seeds for reproducibility (default: 42 123 999)
  --verbose            Detailed output during execution
  --skip-baseline      Skip baseline phase (use existing data)
  --skip-mitigation    Skip mitigation phase (use existing data)
```

## 🎓 For Academic Research

### **Publication-Ready Study**
```bash
# Complete empirical study for papers/thesis
python scripts/run_comprehensive_study.py --baseline-runs 30 --mitigation-runs 10
```

### **Generated Outputs**
- **📄 Comprehensive Report**
- **📊 Quantitative Data**
- **📈 Publication-Quality Visualizations**
- **🎯 Evidence-Based Recommendations**
- **📋 Systematic Classification**
- **💰 Cost-Benefit Analysis**

### **Research Contributions**
- **Techniques**: Reproducible framework with controlled flakiness
- **Practices**: Systematic evaluation protocol for mitigation strategies  
- **Results**: Quantitative effectiveness data and practical recommendations

## 🔬 Framework Extension

### **Adding New Flakiness Types**
1. Create new test file: `tests/test_flaky_newtype.py`
2. Add appropriate markers: `@pytest.mark.flaky`, `@pytest.mark.newtype`
3. Update flakiness profiles in `scripts/classification/flakiness_classifier.py`:

```python
"newtype": FlakynessProfile(
    test_type="newtype",
    description="Your new flakiness description",
    failure_mechanism="Explanation of failure",
    typical_pass_rate=0.6,  # Expected pass rate
    mitigation_effectiveness={
        "retries": 0.3, "mocking": 0.8, 
        "isolation": 0.5, "combined": 0.9
    }
)
```

### **Adding New Mitigation Strategies**
1. Implement strategy method in `scripts/execution/experiment_runner.py`
2. Add to `MitigationRunner` class strategies
3. Update cost definitions in `scripts/analysis/data_analyzer.py`
4. Update visualization logic in `scripts/visualization/chart_generator.py`

## 📚 Data Structure

### Comprehensive Study Data (`comprehensive_study_data.json`)
```json
{
  "study_metadata": {
    "study_type": "comprehensive_flaky_test_analysis",
    "timestamp": "2024-01-01T12:00:00",
    "configuration": { "baseline_runs": 10, "mitigation_runs": 10 }
  },
  "baseline_results": {
    "randomness": {
      "avg_pass_rate": 0.472,
      "flakiness_index": 0.342,
      "total_runs": 90
    }
  },
  "mitigation_results": {
    "retries": {
      "avg_pass_rate": 0.756,
      "avg_execution_time": 2.34,
      "total_runs": 10
    }
  },
  "analysis_results": {
    "mitigation_effectiveness": {
      "retries": {
        "pass_rate_improvement": { "relative_percent": 23.4 },
        "effectiveness_score": 0.634
      }
    },
    "cost_benefit_analysis": {
      "retries": { "roi": 2.45, "recommendation": "Recommended" }
    }
  }
}
```

### CSV Summaries
- **`baseline_summary.csv`**: Pass rates and flakiness indices by type
- **`mitigation_summary.csv`**: Effectiveness and overhead by strategy


## 🤝 Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/new-flaky-type`)
3. Commit changes (`git commit -am 'Add timeout flaky'`)
4. Push to branch (`git push origin feature/new-flaky-type`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details.