# PEMCAFE (Process-based Ecosystem Model for Carbon Assessment in Forest Ecosystems)

## Overview
PEMCAFE (version 0.9, released October 10, 2024) is a process-based ecosystem model designed for carbon assessment in forest ecosystems, with a specific focus on bamboo forests. This model implements comprehensive carbon cycle calculations and provides various ecosystem productivity metrics.

## Key Features
- Comprehensive carbon pool calculations
- Above-ground and below-ground carbon flux estimation
- Two methods for BNPP estimation
- Automated parameter optimization
- Iterative convergence mechanism
- Optional harvested bamboo products consideration

## Model Outputs
- Above-ground Net Primary Production (ANPP)
- Below-ground Net Primary Production (BNPP)
- Total Net Primary Production (TNPP)
- Net Ecosystem Production (NEP)
- Gross Primary Production (GPP)
- Various carbon pool measurements

## System Requirements
### Hardware Requirements
- Minimum 4GB RAM (8GB recommended)
- 1GB free disk space
- Any modern CPU (2GHz or faster recommended)

### Software Requirements
- Python 3.7 or 3.8
- Operating System: Windows 10/11, macOS 10.14+, or Linux
- Required Python packages:
  - pandas
  - numpy
  - scipy

## Complete Installation Guide

### 1. Python Installation
1. Download Python 3.7 or 3.8:
   - Windows: Visit [python.org](https://www.python.org/downloads/)
   - macOS: Use Homebrew: `brew install python@3.8`
   - Linux: `sudo apt-get install python3.8` (Ubuntu/Debian)

2. Verify installation:
   ```bash
   python --version
   ```

### 2. Virtual Environment Setup
```bash
# Windows
python -m venv pemcafe-env
pemcafe-env\Scripts\activate

# macOS/Linux
python3 -m venv pemcafe-env
source pemcafe-env/bin/activate
```

### 3. Package Installation
```bash
pip install pandas numpy scipy
```

Verify installation:
```bash
python -c "import pandas; import numpy; import scipy; print('All packages installed successfully')"
```

## Data Preparation

### Input File Requirements
Create a CSV file with the following columns:

| Column Name | Description | Units | Example Value |
|------------|-------------|--------|---------------|
| Foliages | Leaf biomass | Mg C ha⁻¹ | 2.5 |
| Branches | Branch biomass | Mg C ha⁻¹ | 3.2 |
| Culms | Culm biomass | Mg C ha⁻¹ | 15.6 |
| Stumps | Stump biomass | Mg C ha⁻¹ | 1.8 |
| Rhizomes | Rhizome biomass | Mg C ha⁻¹ | 8.4 |
| Roots | Root biomass | Mg C ha⁻¹ | 4.2 |
| AvgTemp | Average temperature | °C | 25.3 |
| Undergrowth | Undergrowth biomass | Mg C ha⁻¹ | 0.5 |
| Litter_layer | Litter layer mass | Mg C ha⁻¹ | 1.2 |
| SC | Soil carbon | Mg C ha⁻¹ | 45.6 |

### Sample CSV Format
```csv
Foliages,Branches,Culms,Stumps,Rhizomes,Roots,AvgTemp,Undergrowth,Litter_layer,SC
2.5,3.2,15.6,1.8,8.4,4.2,25.3,0.5,1.2,45.6
```

## Model Configuration

### 1. File Setup
1. Create a working directory:
   ```bash
   mkdir pemcafe_project
   cd pemcafe_project
   ```

2. Copy PEMCAFE.py and your input CSV to this directory

### 2. Code Configuration
Open PEMCAFE.py and modify these parameters:

```python
# File paths
input_path = "path/to/your/inputdataforPEMCAFE.csv"
output_path = "path/to/your/optimised_outputresultsforPEMCAFE.csv"

# Model parameters
HBP = 0  # Set to 1 if harvesting bamboo products
BNPPmethod = 1  # 1 for BNG + Dbelow, 0 for BNG + Soil_AR

# Optimization parameters
tolerance = 1e-6
max_iterations = 100
```

## Running the Model

### 1. Basic Execution
```bash
# Navigate to project directory
cd path/to/pemcafe_project

# Activate virtual environment
source pemcafe-env/bin/activate  # or pemcafe-env\Scripts\activate on Windows

# Run the model
python PEMCAFE.py
```

### 2. Monitor Progress
The model will display:
- Optimization progress
- Iteration count
- RMSE values
- Final parameter values

### 3. Check Results
Output will be saved to the specified CSV file with calculated values for:
- All NPP metrics
- Carbon pool sizes
- Flux rates
- Error estimates

## Troubleshooting

### Common Issues and Solutions

1. ImportError:
   ```bash
   pip install --upgrade pandas numpy scipy
   ```

2. File not found error:
   - Check file paths
   - Ensure using correct path separators (/ or \)

3. Memory errors:
   - Close other applications
   - Reduce input data size
   - Increase system swap space

4. Convergence issues:
   - Increase max_iterations
   - Adjust tolerance value
   - Check input data quality

## Support and Contact
For technical support or questions:
1. Check documentation
2. Review error messages
3. Contact your system administrator

---
