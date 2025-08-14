# Module Structure Documentation

## 📁 Directory Structure

```
scripts/
├── run_comprehensive_study.py          # Main orchestrator
├── config/
│   ├── __init__.py
│   └── study_config.py                 # Configuration classes & constants
├── classification/
│   ├── __init__.py  
│   └── flakiness_classifier.py         # 5 flakiness types classification system
├── execution/
│   ├── __init__.py
│   └── experiment_runner.py            # Baseline & mitigation experiment execution
├── analysis/
│   ├── __init__.py
│   └── data_analyzer.py                # Data analysis & metrics calculation
├── visualization/
│   ├── __init__.py
│   └── chart_generator.py              # Publication-quality chart generation
├── reporting/
│   ├── __init__.py
│   └── report_generator.py             # Comprehensive report generation
└── utils/
    ├── __init__.py
    └── helpers.py                      # Shared utility functions
```

## 🎯 Module Responsibilities

### 1. `config/study_config.py`
**Purpose**: Centralized configuration management
- `StudyConfiguration` - Main config dataclass
- `FlakynessProfile` - Profile structure for flakiness types
- Constants for costs, configurations, and defaults

**Key Components**:
```python
StudyConfiguration(baseline_runs=15, mitigation_runs=15, seeds=[42, 123, 999])
IMPLEMENTATION_COSTS = {'retries': 2, 'mocking': 6, 'isolation': 4, 'combined': 8}
BASELINE_CONFIGURATIONS = [stable_only, randomness, timeout, order, external, race, all_flaky]
```

### 2. `classification/flakiness_classifier.py`
**Purpose**: Systematic flakiness classification
- 5 main flakiness types with detailed profiles
- Severity and predictability classification
- Implementation notes for each strategy-type combination

**Key Components**:
```python
FlakynessClassifier.get_flakiness_profiles()  # Returns all 5 types
classify_severity(flakiness_index)            # low/moderate/high/severe
get_implementation_notes(type, strategy)      # Specific guidance
```

### 3. `execution/experiment_runner.py`
**Purpose**: Test execution orchestration
- `BaselineRunner` - Executes baseline experiments across all types
- `MitigationRunner` - Executes 4 mitigation strategies
- Dependency checking and test configuration

**Key Components**:
```python
BaselineRunner(config).run_experiments()     # Phase 1: Baseline
MitigationRunner(config).run_experiments()   # Phase 2: Mitigation
# Handles: retries, mocking, isolation, combined strategies
```

### 4. `analysis/data_analyzer.py`
**Purpose**: Comprehensive data analysis
- Flakiness type analysis with classification
- Mitigation effectiveness calculation
- Cost-benefit analysis with ROI
- Statistical significance testing
- Recommendation generation

**Key Components**:
```python
DataAnalyzer().analyze(baseline_results, mitigation_results)
# Returns: flakiness_classification, mitigation_effectiveness, 
#          cost_benefit_analysis, recommendations
```

### 5. `visualization/chart_generator.py`
**Purpose**: Publication-quality visualizations
- 4 comprehensive chart sets
- Flakiness overview, effectiveness comparison
- Cost-benefit visualization, performance analysis

**Key Components**:
```python
ChartGenerator().create_all_charts(analysis, baseline, mitigation, output_dir)
# Generates: flakiness_classification.png, mitigation_effectiveness.png,
#           cost_benefit_analysis.png, performance_analysis.png
```

### 6. `reporting/report_generator.py`
**Purpose**: Report generation and data persistence
- Comprehensive text report generation
- JSON/CSV data export
- Final summary and recommendations

**Key Components**:
```python
ReportGenerator(start_time, metadata).generate_report(analysis, baseline, mitigation, output_dir)
# Generates: comprehensive_study_report.txt, comprehensive_study_data.json,
#           baseline_summary.csv, mitigation_summary.csv
```

### 7. `utils/helpers.py`
**Purpose**: Shared utility functions
- Random seed management
- Test result parsing
- Effectiveness calculations
- File operations and validation

**Key Components**:
```python
set_random_seeds(seed)                        # Reproducibility
parse_test_result(output_file, ...)           # JSON result parsing
calculate_effectiveness_score(improvement, overhead)  # Scoring
```

### 8. `run_comprehensive_study.py`
**Purpose**: Clean orchestrator - coordinates all modules
- Simplified main class that delegates to modules
- Configuration handling
- Phase coordination
- Error handling

**Key Components**:
```python
class ComprehensiveStudy:
    def run_study(self):
        # Phase 1: Baseline Analysis
        self.baseline_results = self.baseline_runner.run_experiments()
        
        # Phase 2: Mitigation Analysis  
        self.mitigation_results = self.mitigation_runner.run_experiments()
        
        # Phase 3: Analysis
        self.analysis_results = self.analyzer.analyze(baseline, mitigation)
        
        # Phase 4: Visualization & Reporting
        self.chart_generator.create_all_charts(...)
        self.report_generator.generate_report(...)
```

## 🔄 Data Flow

```
Configuration → BaselineRunner → Results
                     ↓
                MitigationRunner → Results  
                     ↓
                DataAnalyzer → Analysis
                     ↓
             ChartGenerator → Visualizations
                     ↓
            ReportGenerator → Final Report
```

## ✅ Benefits Achieved

### **Maintainability**
- **Single Responsibility**: Each module has one clear purpose
- **Reduced Complexity**: Largest module is ~200 lines vs original 1547
- **Easy Navigation**: Functionality grouped logically

### **Testability**
- **Unit Testing**: Each module can be tested independently
- **Mocking**: Clean interfaces enable easy mocking
- **Isolation**: Components don't depend on implementation details

### **Extensibility**
- **New Flakiness Types**: Add to `classification/` module only
- **New Strategies**: Add to `execution/` module only  
- **New Visualizations**: Add to `visualization/` module only
- **New Metrics**: Add to `analysis/` module only

### **Reusability**
- **FlakynessClassifier**: Usable in other projects
- **ChartGenerator**: Configurable for different data
- **DataAnalyzer**: Extensible metrics framework

## 🚀 Usage

```bash
python scripts/run_comprehensive_study.py --baseline-runs 15 --mitigation-runs 15
```

## 🔧 Development

### Adding New Flakiness Type
1. Edit `classification/flakiness_classifier.py`
2. Add profile to `get_flakiness_profiles()`
3. No other changes needed

### Adding New Mitigation Strategy  
1. Edit `execution/experiment_runner.py`
2. Add method to `MitigationRunner`
3. Add to strategies dict
4. Update costs in `config/study_config.py`

### Adding New Analysis
1. Edit `analysis/data_analyzer.py`
2. Add analysis method
3. Update `analyze()` to call new method
