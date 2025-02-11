# PEMCAFE (Process-based Ecosystem Model for Carbon Assessment in Forest Ecosystems)

## Overview
PEMCAFE (version 0.9, released October 10, 2024) is a process-based ecosystem model designed for carbon assessment in forest ecosystems, with a specific focus on forests with unstable root-shoot ratio. This model implements comprehensive carbon cycle calculations and provides various ecosystem productivity metrics.

## Key Features
- Comprehensive carbon pool calculations
- Above-ground and below-ground carbon flux estimation
- Two methods for BNPP estimation
- Automated parameter optimisation
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

### Input File Format (inputdataforPEMCAFE.csv)
Your input CSV file should contain the following columns:

| Column Name | Description | Units | Example Value |
|------------|-------------|--------|---------------|
| t | Time step | years | 0, 1, 2... |
| AvgTemp | Average temperature | °C | 18.6 |
| Foliages | Leaf biomass | Mg C ha⁻¹ | 2.78 |
| Branches | Branch biomass | Mg C ha⁻¹ | 5.03 |
| Culms | Culm biomass | Mg C ha⁻¹ | 28.59 |
| AGC | Above-ground carbon | Mg C ha⁻¹ | 36.4 |
| Root_Shoot_Ratio | Root to shoot ratio | ratio | 0.925549451 |
| Roots | Root biomass | Mg C ha⁻¹ | 6.48 |
| Rhizomes | Rhizome biomass | Mg C ha⁻¹ | 17.175153 |
| Stumps | Stump biomass | Mg C ha⁻¹ | 10.034847 |
| BGC | Below-ground carbon | Mg C ha⁻¹ | 33.69 |
| TC | Total carbon | Mg C ha⁻¹ | 70.09 |
| Litter_layer | Litter layer mass | Mg C ha⁻¹ | 1.35756 |
| SC | Soil carbon | Mg C ha⁻¹ | 70.25 |
| Undergrowth | Undergrowth biomass | Mg C ha⁻¹ | 0 |
| TEC | Total ecosystem carbon | Mg C ha⁻¹ | 141.69756 |

### Sample Input Data
```csv
t,AvgTemp,Foliages,Branches,Culms,AGC,Root_Shoot_Ratio,Roots,Rhizomes,Stumps,BGC,TC,Litter_layer,SC,Undergrowth,TEC
0,18.6,2.78,5.03,28.59,36.4,0.925549451,6.48,17.175153,10.034847,33.69,70.09,1.35756,70.25,0,141.69756
1,18.6,2.99,5.38,31.32,39.69,,,,,,,,,0,
2,18.6,3.13,5.65,33.26,42.04,,,,,,,,,0,
```

### Important Notes
1. **Required Initial Values**: For the first time step (t = 0), you must provide all values
2. **Subsequent Time Steps**: Only these columns are required:
   - t
   - AvgTemp
   - Foliages
   - Branches
   - Culms
   - Undergrowth
3. **Data Format**:
   - Use comma (,) as the delimiter
   - Decimal numbers should use point (.) not comma
   - Missing values can be left empty
   - No spaces after commas
4. **Units**: All biomass and carbon values should be in Mg C ha⁻¹ (Mega grams of carbon per hectare)

### Output Columns
The model will calculate and output all other columns including:
- NPP metrics (LNP, BNP, CNP)
- Decomposition rates (LD, BD, CD)
- Carbon fluxes (Litterfall, ANPP, BNPP, TNPP)
- Respiration values (SR, HR)
- Autotrophic respiration (AR) components
- Net ecosystem production (NEP)


## Model Configuration

### 1. File Setup
1. Create a working directory:
   ```bash
   mkdir pemcafe_project
   cd pemcafe_project
   ```

2. Copy PEMCAFE_ad.py and your input CSV to this directory

### 2. Code Configuration
Open PEMCAFE_ad.py and modify these parameters:

```python
# File paths
input_path = "path/to/your/inputdataforPEMCAFE.csv"
output_path = "path/to/your/optimised_outputresultsforPEMCAFE.csv"

# Model parameters
HBP = 0  # Set to 1 if harvesting bamboo products
BNPPmethod = 1  # 1 for BNG + Dbelow, 0 for BNG + Soil_AR

# Optimisation parameters
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
python PEMCAFE_ad.py
```

### 2. Monitor Progress
The model will display:
- Optimisation progress
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
3. Contact Shitephen (gn03138868＠gmail.com)

---
