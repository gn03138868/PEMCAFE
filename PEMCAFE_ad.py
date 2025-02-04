# PEMCAFE (ver. 0.9 10.Oct.2024)
# ANPP = delta AGC + litterfall 
# but BNPP have different methods 
# 1. delta BGC + Dbelow
# 2. delta BGC + Soil_AR

# combind single time version

import pandas as pd
import numpy as np
import math
from scipy.optimize import minimize

# Read the CSV file
df = pd.read_csv(r"Z:\RF for bamboo\Task C1\inputdataforPEMCAFE.csv")

# Define initial parameters
initial_params = [
    0.32,  # kLitter 
    0.63,  # LTurnoverR #Kobayashi et al., 2022
    0.21,  # BTurnoverR #Kobayashi et al., 2022
    0.18,  # CTurnoverR #Kobayashi et al., 2022
    0.18,  # StTurnoverR #Kobayashi et al., 2022
    0.9 / 8.1,  # RhTurnoverR #Kobayashi et al., 2022
    3.10 / 8.40,  # RoTurnoverR #Kobayashi et al., 2022
    3.87561968569648 / (1.57416255555556 + 3.87561968569648)  # Rratio_Litter_layer #Isagi et al., 1997
]

# Define bounds for parameters (all must be positive)
bounds = [
    (0, None),  # kLitter
    (0, None),  # LTurnoverR
    (0, None),  # BTurnoverR
    (0, None),  # CTurnoverR
    (0, None),  # StTurnoverR
    (0, None),  # RhTurnoverR
    (0, None),  # RoTurnoverR
    (0, 1)     # Rratio_Litter_layer
]

# Constraints: LTurnoverR > BTurnoverR > CTurnoverR and RoTurnoverR > RhTurnoverR
constraints = [
    {'type': 'ineq', 'fun': lambda params: params[1] - params[2]},  # LTurnoverR > BTurnoverR
    {'type': 'ineq', 'fun': lambda params: params[2] - params[3]},  # BTurnoverR > CTurnoverR
    {'type': 'ineq', 'fun': lambda params: params[6] - params[5]}   # RoTurnoverR > RhTurnoverR
]

# Is harvesting bamboo products or not?
# If yes, HBP = 1 else 0
#HBP = 1
HBP = 0

# Which method you would like to estimate BNPP
# If BNG + Dbelow, BNPPmethod=1 else 0 (BNG + Soil_AR)
BNPPmethod=1
#BNPPmethod=0


# Function to calculate values for each row
def calculate_values(row, prev_row, params):
    kLitter, LTurnoverR, BTurnoverR, CTurnoverR, StTurnoverR, RhTurnoverR, RoTurnoverR, Rratio_Litter_layer = params

    results = row.to_dict()  # Start with all original data

    results['LNP'] = row['Foliages'] - prev_row['Foliages'] if prev_row is not None else 0
    results['BNP'] = row['Branches'] - prev_row['Branches'] if prev_row is not None else 0
    results['CNP'] = row['Culms'] - prev_row['Culms'] if prev_row is not None else 0

    results['AGC'] = row['Foliages'] + row['Branches'] + row['Culms']

    results['StNP'] = 0.1955 * results['CNP']
    results['RhNP'] = 1.1162 * abs(results['LNP'])**0.7279 if results['LNP'] != 0 else 0
    results['RoNP'] = 0.9847 * results['RhNP']

    if prev_row is None:
        results['Stumps'] = row['Stumps']
        results['Rhizomes'] = row['Rhizomes']
        results['Roots'] = row['Roots']
    else:
        results['Stumps'] = prev_row['Stumps'] + results['StNP']
        results['Rhizomes'] = prev_row['Rhizomes'] + results['RhNP']
        results['Roots'] = prev_row['Roots'] + results['RoNP']

    results['BGC'] = results['Stumps'] + results['Rhizomes'] + results['Roots']
    results['Root_Shoot_Ratio'] = results['BGC'] / results['AGC'] if results['AGC'] != 0 else 0
    results['TC'] = results['AGC'] + results['BGC']

    results['LD'] = prev_row['Foliages'] * LTurnoverR if prev_row is not None else 0
    results['BD'] = prev_row['Branches'] * BTurnoverR if prev_row is not None else 0
    results['CD'] = prev_row['Culms'] * CTurnoverR if prev_row is not None else 0

    if HBP == 1:
        results['Litterfall'] = results['LD'] + results['BD']  # Exclude `CD`
    else:
        results['Litterfall'] = results['LD'] + results['BD'] + results['CD']  # Include `CD`

    results['ANPP'] = results['LNP'] + results['BNP'] + results['CNP'] + results['Litterfall']

    results['StD'] = prev_row['Stumps'] * StTurnoverR if prev_row is not None else 0
    results['RhD'] = prev_row['Rhizomes'] * RhTurnoverR if prev_row is not None else 0
    results['RoD'] = prev_row['Roots'] * RoTurnoverR if prev_row is not None else 0

    results['Dbelow'] = results['StD'] + results['RhD'] + results['RoD']

    if BNPPmethod == 1:
        results['BNPP'] = results['StNP'] + results['RhNP'] + results['RoNP'] + results['Dbelow']
    else:
        results['BNPP'] = results['StNP'] + results['RhNP'] + results['RoNP'] + results['Soil_AR']    
    
    results['TNPP'] = results['ANPP'] + results['BNPP']

    if results['ANPP'] < 4.17:
        hr_anpp = 4.17
    elif results['ANPP'] > 11.8:
        hr_anpp = 11.8
    else:
        hr_anpp = results['ANPP']
    results['Soil_HR'] = 0.0071 * hr_anpp**3.0772 if results['ANPP'] != 0 else 0

    results['Foliages_AR'] = 1.172/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (row['Foliages']/0.4544 * 1000000) /1000/1000/1000 * 12/44.01) 
    results['Branches_AR'] = 0.215/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (row['Branches']/0.4815 * 1000000) /1000/1000/1000 * 12/44.01)
    results['Culms_AR'] = 0.085/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (row['Culms']/0.4628 * 1000000) /1000/1000/1000 * 12/44.01)
    results['Aboveground_AR'] = results['Foliages_AR'] + results['Branches_AR'] + results['Culms_AR']
    
    results['Roots_AR_ratio'] = (0.088/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Roots']/0.4487 * 1000000) /1000/1000/1000 * 12/44.01))/((0.088/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Roots']/0.4487 * 1000000) /1000/1000/1000 * 12/44.01))+(0.179/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Rhizomes']/0.4354 * 1000000) /1000/1000/1000 * 12/44.01))+(0.085/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Stumps']/0.4628 * 1000000) /1000/1000/1000 * 12/44.01)))

    results['Rhizomes_AR_ratio'] = (0.179/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Rhizomes']/0.4487 * 1000000) /1000/1000/1000 * 12/44.01))/((0.088/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Roots']/0.4487 * 1000000) /1000/1000/1000 * 12/44.01))+(0.179/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Rhizomes']/0.4354 * 1000000) /1000/1000/1000 * 12/44.01))+(0.085/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Stumps']/0.4628 * 1000000) /1000/1000/1000 * 12/44.01)))

    results['Stumps_AR_ratio'] = (0.085/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Stumps']/0.4628 * 1000000) /1000/1000/1000 * 12/44.01))/((0.088/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Roots']/0.4487 * 1000000) /1000/1000/1000 * 12/44.01))+(0.179/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Rhizomes']/0.4354 * 1000000) /1000/1000/1000 * 12/44.01))+(0.085/1.172 * ((1.445 * 10**(-1) * math.exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Stumps']/0.4628 * 1000000) /1000/1000/1000 * 12/44.01)))
    
    results['Soil_AR'] = 0.000006 * results['BGC']**3.3249 
    
    # Calculate and add Roots_AR, Rhizomes_AR, and Stumps_AR to the results
    results['Roots_AR'] = results['Soil_AR'] * results['Roots_AR_ratio']
    results['Rhizomes_AR'] = results['Soil_AR'] * results['Rhizomes_AR_ratio']
    results['Stumps_AR'] = results['Soil_AR'] * results['Stumps_AR_ratio']
    
    results['AR'] = results['Aboveground_AR'] + results['Soil_AR'] 
    
    results['SR'] = results['Soil_AR'] + results['Soil_HR']
    results['NEP_with_Aboveground_Detritus_Litter_layer_HR'] = results['TNPP'] - results['Soil_HR'] if results['TNPP'] != 0 else 0 

    results['Litter_layer'] = (prev_row['Litter_layer'] + results['Litterfall']) * kLitter if prev_row is not None else row['Litter_layer']
    results['DLitter_layer'] = results['Litter_layer'] * kLitter
    results['Litter_layer_HR'] = results['Litter_layer'] * Rratio_Litter_layer

    results['HR'] = results['Soil_HR'] + results['Litter_layer_HR']
    results['NEP'] = results['NEP_with_Aboveground_Detritus_Litter_layer_HR'] - results['Litter_layer_HR'] if results['TNPP'] != 0 else 0

    if prev_row is not None:
        results['SC'] = prev_row['SC'] + results['Dbelow'] - results['Soil_HR'] + results['DLitter_layer']
    else:
        results['SC'] = row['SC']
        
    results['dSC'] = results['SC'] - prev_row['SC'] if prev_row is not None else 0
    results['TEC'] = results['TC'] + results['Litter_layer'] + results['SC'] + row['Undergrowth']
    results['NEP_from_dTEC'] = results['TEC'] - prev_row['TEC'] if prev_row is not None else 0
    
    results['GPP'] = results['TNPP'] + results['AR'] 

    return results

# Function to run the model with iteration until convergence
def run_model_until_convergence(params, tolerance=1e-6, max_iterations=100):
    # Initialize iteration variables
    prev_results = None
    iteration = 0
    converged = False
    
    # Start iteration loop
    while not converged and iteration < max_iterations:
        # Calculate results for current iteration
        results = []
        prev_row = None

        for i in range(len(df)):
            updated_values = calculate_values(df.iloc[i], prev_row, params)
            results.append(updated_values)
            prev_row = updated_values
        
        current_results = pd.DataFrame(results)
        
        # Check for convergence if this is not the first iteration
        if prev_results is not None:
            # Calculate RMSE between the current and previous iteration for NEP
            #rmse = np.sqrt(np.mean((current_results['NEP'] - prev_results['NEP'])**2))
            rmse = np.sqrt(np.mean((results['NEP_from_dTEC'] - results['NEP'])**2))

            if rmse < tolerance:
                converged = True
        
        # Update prev_results to current_results for the next iteration comparison
        prev_results = current_results
        iteration += 1

        print(f"Iteration {iteration}, RMSE: {rmse}")

    if iteration == max_iterations:
        print("Warning: Maximum iterations reached without full convergence.")
    
    return current_results


# Step 1: Optimise the parameters using the initial run
result = minimize(objective_function, initial_params, method='Nelder-Mead')

# Step 2: Get the optimised parameters
optimised_params = result.x
print("Optimised parameters:", optimised_params)

# Step 3: Run the model with the optimised parameters to get final results
final_results = run_model(optimised_params)

# Step 4: Save the results
final_results.to_csv(r"Z:\RF for bamboo\Task C1\optimised_outputresultsforPEMCAFE.csv", index=False)
print("Optimisation complete. Results saved to 'optimised_outputresultsforPEMCAFE.csv'.")
