# PEMCAFE (ver. 0.96 07 July 2025 stable) with 95% CI estimation via sd from AGC
# ANPP = delta AGC + litterfall 
# but BNPP have different methods 
# 1. delta BGC + Dbelow
# 2. delta BGC + Soil_AR

# combined single time version with Monte Carlo simulation for CI estimation
# user interface built
# t=0, flux of C need to be 0

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import math
from scipy.optimize import minimize
from scipy import stats
import threading
import os

class PEMCAFEModelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PEMCAFE Model Controller (ver. 0.96)")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.df = None
        self.results = None
        self.optimized_params = None
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_file_tab()
        self.create_parameters_tab()
        self.create_input_uncertainty_tab()
        self.create_model_settings_tab()
        self.create_results_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_file_tab(self):
        """File operations tab"""
        file_frame = ttk.Frame(self.notebook)
        self.notebook.add(file_frame, text="File & Data")
        
        # File selection
        ttk.Label(file_frame, text="Input CSV File:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(pady=5)
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_select_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_select_frame, text="Load", command=self.load_file).pack(side=tk.LEFT, padx=5)
        
        # Data preview
        ttk.Label(file_frame, text="Data Preview:", font=('Arial', 12, 'bold')).pack(pady=(20,5))
        
        # Create treeview for data preview
        self.data_tree = ttk.Treeview(file_frame)
        self.data_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbars for treeview
        v_scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(file_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.data_tree.configure(xscrollcommand=h_scrollbar.set)
        
    def create_parameters_tab(self):
        """Model parameters tab"""
        param_frame = ttk.Frame(self.notebook)
        self.notebook.add(param_frame, text="Model Parameters")
        
        # Create scrollable frame
        canvas = tk.Canvas(param_frame)
        scrollbar = ttk.Scrollbar(param_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Initial parameters
        ttk.Label(scrollable_frame, text="Initial Model Parameters", font=('Arial', 14, 'bold')).pack(pady=10)
        
        self.param_vars = {}
        initial_values = {
            'kLitter': 0.32,
            'LTurnoverR': 0.63,
            'BTurnoverR': 0.21,
            'CTurnoverR': 0.18,
            'StTurnoverR': 0.18,
            'RhTurnoverR': 0.9/8.1,
            'RoTurnoverR': 3.10/8.40,
            'Rratio_Litter_layer': 3.87561968569648/(1.57416255555556 + 3.87561968569648)
        }
        
        param_descriptions = {
            'kLitter': 'Litter decomposition rate',
            'LTurnoverR': 'Leaf turnover rate', #(Kobayashi et al., 2022)
            'BTurnoverR': 'Branch turnover rate', 
            'CTurnoverR': 'Culm turnover rate',
            'StTurnoverR': 'Stump turnover rate',
            'RhTurnoverR': 'Rhizome turnover rate',
            'RoTurnoverR': 'Root turnover rate',
            'Rratio_Litter_layer': 'Litter layer respiration ratio' #(Isagi et al., 1997)
        }
        
        for param, initial_val in initial_values.items():
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            ttk.Label(frame, text=f"{param}:", width=20).pack(side=tk.LEFT)
            var = tk.DoubleVar(value=initial_val)
            self.param_vars[param] = var
            
            entry = ttk.Entry(frame, textvariable=var, width=15)
            entry.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(frame, text=param_descriptions[param], foreground='gray').pack(side=tk.LEFT, padx=10)
        
        # Parameter bounds
        ttk.Label(scrollable_frame, text="Parameter Bounds", font=('Arial', 14, 'bold')).pack(pady=(20,10))
        
        self.bounds_vars = {}
        default_bounds = {
            'kLitter': (0, 1),
            'LTurnoverR': (0, 2),
            'BTurnoverR': (0, 2),
            'CTurnoverR': (0, 2),
            'StTurnoverR': (0, 2),
            'RhTurnoverR': (0, 1),
            'RoTurnoverR': (0, 1),
            'Rratio_Litter_layer': (0, 1)
        }
        
        for param in initial_values.keys():
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=20, pady=3)
            
            ttk.Label(frame, text=f"{param} bounds:", width=20).pack(side=tk.LEFT)
            
            lower_var = tk.DoubleVar(value=default_bounds[param][0])
            upper_var = tk.DoubleVar(value=default_bounds[param][1] if default_bounds[param][1] is not None else 10)
            
            ttk.Label(frame, text="Min:").pack(side=tk.LEFT, padx=5)
            ttk.Entry(frame, textvariable=lower_var, width=10).pack(side=tk.LEFT, padx=2)
            
            ttk.Label(frame, text="Max:").pack(side=tk.LEFT, padx=5)
            ttk.Entry(frame, textvariable=upper_var, width=10).pack(side=tk.LEFT, padx=2)
            
            self.bounds_vars[param] = (lower_var, upper_var)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_input_uncertainty_tab(self):
        """Input uncertainty tab"""
        uncertainty_frame = ttk.Frame(self.notebook)
        self.notebook.add(uncertainty_frame, text="Input Uncertainty")
        
        ttk.Label(uncertainty_frame, text="Standard Deviations for Input Variables", font=('Arial', 14, 'bold')).pack(pady=10)
        
        self.sd_vars = {}
        default_sds = {
            'Foliages': 0.3,
            'Branches': 0.7,
            'Culms': 3.2,
            'Roots': 0.4,
            'Rhizomes': 0.3,
            'Stumps': 1.1
        }
        
        for var, default_sd in default_sds.items():
            frame = ttk.Frame(uncertainty_frame)
            frame.pack(fill=tk.X, padx=50, pady=10)
            
            ttk.Label(frame, text=f"{var} SD:", width=15, font=('Arial', 11)).pack(side=tk.LEFT)
            sd_var = tk.DoubleVar(value=default_sd)
            self.sd_vars[var] = sd_var
            
            ttk.Entry(frame, textvariable=sd_var, width=15).pack(side=tk.LEFT, padx=10)
            ttk.Label(frame, text="Standard deviation for Monte Carlo simulation", foreground='gray').pack(side=tk.LEFT, padx=10)
    
    def create_model_settings_tab(self):
        """Model settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Model Settings")
        
        # Model options
        ttk.Label(settings_frame, text="Model Configuration", font=('Arial', 14, 'bold')).pack(pady=20)
        
        # Harvesting bamboo products
        harvesting_frame = ttk.Frame(settings_frame)
        harvesting_frame.pack(fill=tk.X, padx=50, pady=10)
        
        ttk.Label(harvesting_frame, text="Harvesting Woody Products (HWP) or Harvesting Bamboo Products (HBP) :", width=30).pack(side=tk.LEFT)
        self.hbp_var = tk.IntVar(value=0)
        ttk.Radiobutton(harvesting_frame, text="No (0)", variable=self.hbp_var, value=0).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(harvesting_frame, text="Yes (1)", variable=self.hbp_var, value=1).pack(side=tk.LEFT, padx=10)
        
        # BNPP method
        bnpp_frame = ttk.Frame(settings_frame)
        bnpp_frame.pack(fill=tk.X, padx=50, pady=10)
        
        ttk.Label(bnpp_frame, text="BNPP Estimation Method:", width=30).pack(side=tk.LEFT)
        self.bnpp_method_var = tk.IntVar(value=1)
        ttk.Radiobutton(bnpp_frame, text="BGC + Dbelow (1)", variable=self.bnpp_method_var, value=1).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(bnpp_frame, text="BGC + Soil_AR (0)", variable=self.bnpp_method_var, value=0).pack(side=tk.LEFT, padx=10)
        
        # Monte Carlo settings
        ttk.Label(settings_frame, text="Monte Carlo Simulation", font=('Arial', 14, 'bold')).pack(pady=(40,20))
        
        mc_frame = ttk.Frame(settings_frame)
        mc_frame.pack(fill=tk.X, padx=50, pady=10)
        
        ttk.Label(mc_frame, text="Number of Simulations:", width=20).pack(side=tk.LEFT)
        self.n_simulations_var = tk.IntVar(value=1000)
        ttk.Entry(mc_frame, textvariable=self.n_simulations_var, width=15).pack(side=tk.LEFT, padx=10)
        
        # Confidence level
        ci_frame = ttk.Frame(settings_frame)
        ci_frame.pack(fill=tk.X, padx=50, pady=10)
        
        ttk.Label(ci_frame, text="Confidence Level:", width=20).pack(side=tk.LEFT)
        self.confidence_level_var = tk.DoubleVar(value=0.95)
        ttk.Entry(ci_frame, textvariable=self.confidence_level_var, width=15).pack(side=tk.LEFT, padx=10)
        
        # Optimisation settings
        ttk.Label(settings_frame, text="Optimisation Settings", font=('Arial', 14, 'bold')).pack(pady=(40,20))
        
        opt_frame = ttk.Frame(settings_frame)
        opt_frame.pack(fill=tk.X, padx=50, pady=10)
        
        ttk.Label(opt_frame, text="Optimisation Method:", width=20).pack(side=tk.LEFT)
        self.opt_method_var = tk.StringVar(value="Nelder-Mead")
        method_combo = ttk.Combobox(opt_frame, textvariable=self.opt_method_var, width=15)
        method_combo['values'] = ("Nelder-Mead", "L-BFGS-B", "TNC", "SLSQP")
        method_combo.pack(side=tk.LEFT, padx=10)
        
        # Run buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(pady=40)
        
        ttk.Button(button_frame, text="Run Optimisation Only", command=self.run_optimisation, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Run Full Analysis (with MC)", command=self.run_full_analysis, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=10)
        
    def create_results_tab(self):
        """Results display tab"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results")
        
        # Results display area
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=30)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        # Export button
        export_frame = ttk.Frame(results_frame)
        export_frame.pack(pady=10)
        
        ttk.Button(export_frame, text="Export Results to CSV", command=self.export_results).pack()
        
    def browse_file(self):
        """Browse for input CSV file"""
        filename = filedialog.askopenfilename(
            title="Select Input CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            
    def load_file(self):
        """Load and preview the CSV file"""
        try:
            filepath = self.file_path_var.get()
            if not filepath:
                messagebox.showerror("Error", "Please select a file first")
                return
                
            self.df = pd.read_csv(filepath)
            self.display_data_preview()
            self.status_var.set(f"Loaded {len(self.df)} rows from {os.path.basename(filepath)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            
    def display_data_preview(self):
        """Display data preview in treeview"""
        if self.df is None:
            return
            
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
            
        # Set up columns
        self.data_tree["columns"] = list(self.df.columns)
        self.data_tree["show"] = "headings"
        
        for col in self.data_tree["columns"]:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100)
            
        # Insert data (show first 20 rows)
        for index, row in self.df.head(20).iterrows():
            self.data_tree.insert("", "end", values=list(row))
            
    def get_model_parameters(self):
        """Get current model parameters from GUI"""
        params = []
        param_names = ['kLitter', 'LTurnoverR', 'BTurnoverR', 'CTurnoverR', 
                      'StTurnoverR', 'RhTurnoverR', 'RoTurnoverR', 'Rratio_Litter_layer']
        
        for name in param_names:
            params.append(self.param_vars[name].get())
            
        return params
    
    def get_parameter_bounds(self):
        """Get parameter bounds from GUI"""
        bounds = []
        param_names = ['kLitter', 'LTurnoverR', 'BTurnoverR', 'CTurnoverR', 
                      'StTurnoverR', 'RhTurnoverR', 'RoTurnoverR', 'Rratio_Litter_layer']
        
        for name in param_names:
            lower, upper = self.bounds_vars[name]
            bounds.append((lower.get(), upper.get()))
            
        return bounds
    
    def get_input_sds(self):
        """Get input standard deviations from GUI"""
        return {var: self.sd_vars[var].get() for var in self.sd_vars}
    
    def calculate_values(self, row, prev_row, params):
        """Calculate values for each row - same as original function"""
        
        # 添加保護性檢查
        def safe_divide(a, b):
            return a / b if abs(b) > 1e-10 else 0.0
    
        def safe_exp(x):
            try:
                return math.exp(x)
            except:
                return 0.0
            
        # 初始化prev_row為全零字典（如果為None）
        if prev_row is None:
            # 創建包含所有必要字段的默認prev_row
            default_vals = {col: 0.0 for col in self.df.columns}
            default_vals.update({
                'Litter_layer': row['Litter_layer'] if 'Litter_layer' in row else 0.01,
                'SC': row['SC'] if 'SC' in row else 0.01,
                'Foliages': row['Foliages'] if 'Foliages' in row else 0.01,
                'Branches': row['Branches'] if 'Branches' in row else 0.01,
                'Culms': row['Culms'] if 'Culms' in row else 0.01,
                'Stumps': row['Stumps'] if 'Stumps' in row else 0.01,
                'Rhizomes': row['Rhizomes'] if 'Rhizomes' in row else 0.01,
                'Roots': row['Roots'] if 'Roots' in row else 0.01,
            })
            prev_row = pd.Series(default_vals)
        
        kLitter, LTurnoverR, BTurnoverR, CTurnoverR, StTurnoverR, RhTurnoverR, RoTurnoverR, Rratio_Litter_layer = params
        
        results = row.to_dict()
        

        
        # Net production calculations
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
        results['Root_Shoot_Ratio'] = safe_divide(results['BGC'], results['AGC'])
        results['TC'] = results['AGC'] + results['BGC']
        
        # Death calculations
        results['LD'] = prev_row['Foliages'] * LTurnoverR if prev_row is not None else 0
        results['BD'] = prev_row['Branches'] * BTurnoverR if prev_row is not None else 0
        results['CD'] = prev_row['Culms'] * CTurnoverR if prev_row is not None else 0
        
        HBP = self.hbp_var.get()
        if HBP == 1:
            results['Litterfall'] = results['LD'] + results['BD']
        else:
            results['Litterfall'] = results['LD'] + results['BD'] + results['CD']
        
        results['ANPP'] = results['LNP'] + results['BNP'] + results['CNP'] + results['Litterfall']
        
        results['StD'] = prev_row['Stumps'] * StTurnoverR if prev_row is not None else 0
        results['RhD'] = prev_row['Rhizomes'] * RhTurnoverR if prev_row is not None else 0
        results['RoD'] = prev_row['Roots'] * RoTurnoverR if prev_row is not None else 0
        
        results['Dbelow'] = results['StD'] + results['RhD'] + results['RoD']
        
        BNPPmethod = self.bnpp_method_var.get()
        if BNPPmethod == 1:
            results['BNPP'] = results['StNP'] + results['RhNP'] + results['RoNP'] + results['Dbelow']
        else:
            results['BNPP'] = results['StNP'] + results['RhNP'] + results['RoNP'] + results['Soil_AR']
        
        results['TNPP'] = results['ANPP'] + results['BNPP']
        
        # Soil HR calculation
        if results['ANPP'] < 4.17:
            hr_anpp = 4.17
        elif results['ANPP'] > 11.8:
            hr_anpp = 11.8
        else:
            hr_anpp = results['ANPP']
        results['Soil_HR'] = 0.0071 * hr_anpp**3.0772 if results['ANPP'] != 0 else 0
        
        # Autotrophic respiration calculations
        results['Foliages_AR'] = 1.172/1.172 * ((1.445 * 10**(-1) * safe_exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (row['Foliages']/0.4544 * 1000000) /1000/1000/1000 * 12/44.01)
        results['Branches_AR'] = 0.215/1.172 * ((1.445 * 10**(-1) * safe_exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (row['Branches']/0.4815 * 1000000) /1000/1000/1000 * 12/44.01)
        results['Culms_AR'] = 0.085/1.172 * ((1.445 * 10**(-1) * safe_exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (row['Culms']/0.4628 * 1000000) /1000/1000/1000 * 12/44.01)
        results['Aboveground_AR'] = results['Foliages_AR'] + results['Branches_AR'] + results['Culms_AR']
        
        # Soil AR ratios
        denominator = ((0.088/1.172 * ((1.445 * 10**(-1) * safe_exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Roots']/0.4487 * 1000000) /1000/1000/1000 * 12/44.01))+
                      (0.179/1.172 * ((1.445 * 10**(-1) * safe_exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Rhizomes']/0.4354 * 1000000) /1000/1000/1000 * 12/44.01))+
                      (0.085/1.172 * ((1.445 * 10**(-1) * safe_exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Stumps']/0.4628 * 1000000) /1000/1000/1000 * 12/44.01)))
        
        if abs(denominator) > 1e-10:
            results['Roots_AR_ratio'] = (0.088/1.172 * ((1.445 * 10**(-1) * safe_exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Roots']/0.4487 * 1000000) /1000/1000/1000 * 12/44.01)) / denominator
            results['Rhizomes_AR_ratio'] = (0.179/1.172 * ((1.445 * 10**(-1) * safe_exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Rhizomes']/0.4354 * 1000000) /1000/1000/1000 * 12/44.01)) / denominator
            results['Stumps_AR_ratio'] = (0.085/1.172 * ((1.445 * 10**(-1) * safe_exp(7.918*10**(-2)*row['AvgTemp'])) * 365*24 * (results['Stumps']/0.4628 * 1000000) /1000/1000/1000 * 12/44.01)) / denominator
        else:
            results['Roots_AR_ratio'] = 0
            results['Rhizomes_AR_ratio'] = 0
            results['Stumps_AR_ratio'] = 0
        
        results['Soil_AR'] = 0.000006 * results['BGC']**3.3249
        
        results['Roots_AR'] = results['Soil_AR'] * results['Roots_AR_ratio']
        results['Rhizomes_AR'] = results['Soil_AR'] * results['Rhizomes_AR_ratio']
        results['Stumps_AR'] = results['Soil_AR'] * results['Stumps_AR_ratio']
        
        results['AR'] = results['Aboveground_AR'] + results['Soil_AR']
        results['SR'] = results['Soil_AR'] + results['Soil_HR']
        results['NEP_with_Aboveground_Detritus_Litter_layer_HR'] = results['TNPP'] - results['Soil_HR'] if results['TNPP'] != 0 else 0
        
        # Litter layer calculations
        results['Litter_layer'] = (prev_row['Litter_layer'] + results['Litterfall']) * kLitter if prev_row is not None else row['Litter_layer']
        results['DLitter_layer'] = results['Litter_layer'] * kLitter
        results['Litter_layer_HR'] = results['Litter_layer'] * Rratio_Litter_layer
        
        results['HR'] = results['Soil_HR'] + results['Litter_layer_HR']
        results['NEP'] = results['NEP_with_Aboveground_Detritus_Litter_layer_HR'] - results['Litter_layer_HR'] if results['TNPP'] != 0 else 0
        
        # Soil carbon
        if prev_row is not None:
            results['SC'] = prev_row['SC'] + results['Dbelow'] - results['Soil_HR'] + results['DLitter_layer']
        else:
            results['SC'] = row['SC']
        
        results['dSC'] = results['SC'] - prev_row['SC'] if prev_row is not None else 0
        results['TEC'] = results['TC'] + results['Litter_layer'] + results['SC'] + row['Undergrowth']
        results['NEP_from_dTEC'] = results['TEC'] - prev_row['TEC'] if prev_row is not None else 0
        
        results['GPP'] = results['TNPP'] + results['AR']


        # 檢查是否為初始 t0
        is_initial = (prev_row is None)
        
        return results
    
    
    def run_model(self, params, input_df=None):
        """Run the model with given parameters"""
        if input_df is None:
            input_df = self.df
        
        if input_df is None:
            raise ValueError("No input data loaded")
        
        results = []
        prev_row = None
        
        for i in range(len(input_df)):
            updated_values = self.calculate_values(input_df.iloc[i], prev_row, params)
            results.append(updated_values)
            prev_row = updated_values
        
        return pd.DataFrame(results)
    
    def objective_function(self, params):
        """Objective function for optimisation"""
        try:
            results = self.run_model(params)
            if len(results) > 1:
                rmse = np.sqrt(np.mean((results['NEP_from_dTEC'].iloc[1:] - results['NEP'].iloc[1:])**2))
                return rmse
            else:
                return 1e6
        except:
            return 1e6
    
    def run_optimisation(self):
        """Run optimisation only"""
        if self.df is None:
            messagebox.showerror("Error", "Please load input data first")
            return
        
        def optimise():
            try:
                self.status_var.set("Running optimisation...")
                self.root.update()
                
                initial_params = self.get_model_parameters()
                bounds = self.get_parameter_bounds()
                
                # Define constraints
                constraints = [
                    {'type': 'ineq', 'fun': lambda params: params[1] - params[2]},  # LTurnoverR > BTurnoverR
                    {'type': 'ineq', 'fun': lambda params: params[2] - params[3]},  # BTurnoverR > CTurnoverR
                    {'type': 'ineq', 'fun': lambda params: params[6] - params[5]}   # RoTurnoverR > RhTurnoverR
                ]
                
                result = minimize(self.objective_function, initial_params, 
                                method=self.opt_method_var.get(), 
                                bounds=bounds, constraints=constraints)
                
                self.optimized_params = result.x
                
                # Run model with optimised parameters
                self.results = self.run_model(self.optimized_params)
                
                # Display results
                self.display_optimisation_results(result)
                
                self.status_var.set("Optimisation completed successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Optimisation failed: {str(e)}")
                self.status_var.set("Optimisation failed")
        
        # Run in separate thread to prevent GUI freezing
        threading.Thread(target=optimise, daemon=True).start()
    
    def run_full_analysis(self):
        """Run full analysis with Monte Carlo simulation"""
        if self.df is None:
            messagebox.showerror("Error", "Please load input data first")
            return
        
        def full_analysis():
            try:
                self.status_var.set("Running full analysis...")
                self.root.update()
                
                # First run optimisation
                initial_params = self.get_model_parameters()
                bounds = self.get_parameter_bounds()
                
                constraints = [
                    {'type': 'ineq', 'fun': lambda params: params[1] - params[2]},
                    {'type': 'ineq', 'fun': lambda params: params[2] - params[3]},
                    {'type': 'ineq', 'fun': lambda params: params[6] - params[5]}
                ]
                
                self.status_var.set("Running optimisation...")
                self.root.update()
                
                result = minimize(self.objective_function, initial_params, 
                                method=self.opt_method_var.get(), 
                                bounds=bounds, constraints=constraints)
                
                self.optimized_params = result.x
                
                # Run Monte Carlo simulation
                self.status_var.set("Running Monte Carlo simulation...")
                self.root.update()
                
                n_simulations = self.n_simulations_var.get()
                all_mc_results = self.run_monte_carlo_simulation(self.optimized_params, n_simulations)
                
                # Calculate confidence intervals
                self.status_var.set("Calculating confidence intervals...")
                self.root.update()
                
                confidence_level = self.confidence_level_var.get()
                ci_results = self.calculate_confidence_intervals(all_mc_results, confidence_level)
                
                # Get base results
                base_results = self.run_model(self.optimized_params)
                
                # Create final results with CI
                self.results = self.create_final_results_with_ci(base_results, ci_results)
                
                # Display results
                self.display_full_analysis_results(result, ci_results)
                
                self.status_var.set("Full analysis completed successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Full analysis failed: {str(e)}")
                self.status_var.set("Full analysis failed")
        
        # Run in separate thread
        threading.Thread(target=full_analysis, daemon=True).start()
    
    def generate_perturbed_data(self, original_df, sds):
        """Generate perturbed input data based on standard deviations"""
        perturbed_df = original_df.copy()
        
        for var in sds.keys():
            if var in perturbed_df.columns:
                original_values = perturbed_df[var].values
                random_perturbations = np.random.normal(0, sds[var], len(original_values))
                perturbed_values = original_values + random_perturbations
                # 根據變量類型應用不同的約束
                if var in ['Foliages', 'Branches', 'Culms', 'Roots', 'Rhizomes', 'Stumps']:
                    # 生物量變量應為非負
                    perturbed_values = np.maximum(perturbed_values, 0.01)
                elif var == 'AvgTemp':
                    # 溫度應在合理範圍內
                    perturbed_values = np.clip(perturbed_values, -10, 50)
                elif var in ['Litter_layer', 'SC']:
                    # 土壤和凋落物應為非負
                    perturbed_values = np.maximum(perturbed_values, 0.01)
                    
                perturbed_df[var] = perturbed_values
        
        return perturbed_df
    
    def run_monte_carlo_simulation(self, params, n_simulations):
        """Run Monte Carlo simulation"""
        input_sds = self.get_input_sds()
        all_results = []
        error_log = []
        
        for i in range(n_simulations):
            if i % 100 == 0:
                self.status_var.set(f"Monte Carlo simulation: {i+1}/{n_simulations}")
                self.root.update()
            
            try:
                perturbed_df = self.generate_perturbed_data(self.df, input_sds)
                result = self.run_model(params, perturbed_df)
            # 檢查結果是否有效
                if result.isnull().values.any():
                    error_msg = f"Simulation {i+1} contains NaN values"
                    error_log.append(error_msg)
                else:
                    all_results.append(result)
            except Exception as e:
                error_msg = f"Simulation {i+1} failed: {str(e)}"
                error_log.append(error_msg)
    
        # 保存錯誤日誌
        if error_log:
            with open("monte_carlo_errors.log", "w") as f:
                f.write("\n".join(error_log))
    
        return all_results
    
    def calculate_confidence_intervals(self, all_results, confidence_level=0.95):
        """Calculate confidence intervals from Monte Carlo results"""
        if len(all_results) == 0:
            return None
        
        # 清理結果 - 替換NaN為0
        for result in all_results:
            result.fillna(0, inplace=True)
        
        output_columns = [col for col in all_results[0].columns 
                         if col not in ['t', 'AvgTemp', 'Undergrowth']]
    
        ci_results = {}
        alpha = 1 - confidence_level
    
        for col in output_columns:
            col_values = []
            for result in all_results:
                if col in result.columns:
                    col_values.append(result[col].values)
        
            if col_values:
                col_array = np.array(col_values)
            
                # 方法1：使用t分布置信區間（推薦）
                mean_values = np.mean(col_array, axis=0)
                std_values = np.std(col_array, axis=0, ddof=1)  # 使用樣本標準差
                n = len(col_values)
            
                # 使用t分布計算置信區間
                t_value = stats.t.ppf(1 - alpha/2, df=n-1)
                margin_of_error = t_value * std_values / np.sqrt(n)
            
                lower_ci = mean_values - margin_of_error
                upper_ci = mean_values + margin_of_error
            
                # 方法2：百分位數方法（作為備選）
                lower_percentile = (alpha/2) * 100
                upper_percentile = (1 - alpha/2) * 100
                percentile_lower = np.percentile(col_array, lower_percentile, axis=0)
                percentile_upper = np.percentile(col_array, upper_percentile, axis=0)
            
                ci_results[col] = {
                    'mean': mean_values,
                    'std': std_values,
                    'lower_ci': lower_ci,
                    'upper_ci': upper_ci,
                    'percentile_lower': percentile_lower,
                    'percentile_upper': percentile_upper,
                    'n_simulations': n
                }
        
        return ci_results

    def display_full_analysis_results(self, optimisation_result, ci_results):
        """Display full analysis results with confidence intervals"""
        self.results_text.delete(1.0, tk.END)
    
        param_names = ['kLitter', 'LTurnoverR', 'BTurnoverR', 'CTurnoverR', 
                      'StTurnoverR', 'RhTurnoverR', 'RoTurnoverR', 'Rratio_Litter_layer']
    
        results_text = "PEMCAFE Model Full Analysis Results\n"
        results_text += "=" * 60 + "\n\n"
    
        # Optimisation results
        results_text += "OPTIMISATION RESULTS:\n"
        results_text += f"Status: {'Success' if optimisation_result.success else 'Failed'}\n"
        results_text += f"Method: {self.opt_method_var.get()}\n"
        results_text += f"Final Objective Value: {optimisation_result.fun:.6f}\n\n"
    
        results_text += "Optimised Parameters:\n"
        for i, (name, value) in enumerate(zip(param_names, self.optimized_params)):
            results_text += f"  {name:20}: {value:.6f}\n"
    
        # Monte Carlo results
        results_text += f"\n\nMONTE CARLO SIMULATION RESULTS:\n"
        results_text += f"Number of Simulations: {self.n_simulations_var.get()}\n"
        results_text += f"Confidence Level: {self.confidence_level_var.get()*100:.0f}%\n\n"
    
        if ci_results:
            results_text += f"Summary of {self.confidence_level_var.get()*100:.0f}% Confidence Intervals for Key Variables:\n"
            results_text += "Method: Mean ± t * SE (t-distribution based)\n"
            results_text += "-" * 80 + "\n"
            results_text += f"{'Variable':<12} {'Mean':<12} {'Std':<12} {'95% CI Lower':<15} {'95% CI Upper':<15}\n"
            results_text += "-" * 80 + "\n"
        
            key_vars = ['ANPP', 'BNPP', 'TNPP', 'NEP', 'GPP', 'SR', 'AGC', 'BGC']
            for var in key_vars:
                if var in ci_results:
                    mean_val = np.mean(ci_results[var]['mean'])
                    std_val = np.mean(ci_results[var]['std'])
                    mean_lower = np.mean(ci_results[var]['lower_ci'])
                    mean_upper = np.mean(ci_results[var]['upper_ci'])
                
                    results_text += f"{var:<12} {mean_val:<12.3f} {std_val:<12.3f} {mean_lower:<15.3f} {mean_upper:<15.3f}\n"
        
            # 添加百分位數方法的結果作為比較
            results_text += f"\n\nComparison with Percentile Method:\n"
            results_text += "-" * 80 + "\n"
            results_text += f"{'Variable':<12} {'Mean':<12} {'Percentile Lower':<18} {'Percentile Upper':<18}\n"
            results_text += "-" * 80 + "\n"
        
            for var in key_vars:
                if var in ci_results:
                    mean_val = np.mean(ci_results[var]['mean'])
                    perc_lower = np.mean(ci_results[var]['percentile_lower'])
                    perc_upper = np.mean(ci_results[var]['percentile_upper'])
                
                    results_text += f"{var:<12} {mean_val:<12.3f} {perc_lower:<18.3f} {perc_upper:<18.3f}\n"
    
        # Model settings summary
        results_text += f"\n\nMODEL SETTINGS:\n"
        results_text += f"Harvesting Bamboo Products (HBP): {self.hbp_var.get()}\n"
        results_text += f"BNPP Method: {'BGC + Dbelow' if self.bnpp_method_var.get() == 1 else 'BGC + Soil_AR'}\n"
    
        results_text += f"\n\nInput Data Summary:\n"
        results_text += f"Number of time points: {len(self.df) if self.df is not None else 'N/A'}\n"
        if self.df is not None:
            results_text += f"Data columns: {', '.join(self.df.columns.tolist())}\n"
    
        self.results_text.insert(tk.END, results_text)
    
        # Switch to results tab
        self.notebook.select(4)
    
    def create_final_results_with_ci(self, base_results, ci_results):
        """Create final results DataFrame with confidence intervals"""
        
        final_results = base_results.copy()
        

        is_initial = (base_results['t'] == base_results['t'].min())
    
        # t0 flux need to be 0
        flux_vars = [
            'LNP', 'BNP', 'CNP', 'StNP', 'RhNP', 'RoNP',
            'ANPP', 'BNPP', 'TNPP', 'LD', 'BD', 'CD',
            'Litterfall', 'StD', 'RhD', 'RoD', 'Dbelow',
            'NEP', 'NEP_with_Aboveground_Detritus_Litter_layer_HR',
            'NEP_from_dTEC', 'dSC', 'DLitter_layer', 'GPP',
            'SR', 'Litter_layer_HR', 'Soil_HR', 'HR',
            'Foliages_AR', 'Branches_AR', 'Culms_AR', 'Aboveground_AR',
            'Soil_AR', 'AR', 'Roots_AR', 'Rhizomes_AR', 'Stumps_AR',
            'Roots_AR_ratio', 'Rhizomes_AR_ratio', 'Stumps_AR_ratio'
        ]
    
        # t0 flux must be 0
        for var in flux_vars:
            if var in final_results.columns:
                final_results.loc[is_initial, var] = 0.0
        
        # t0 CI also must be 0
        suffixes = [
            '_MC_mean', '_MC_std', '_t_lower_95CI',
            '_t_upper_95CI', '_percentile_lower_95CI',
            '_percentile_upper_95CI'
        ]
    
        for var in flux_vars:
            for suffix in suffixes:
                col_name = f"{var}{suffix}"
                if col_name in final_results.columns:
                    final_results.loc[is_initial, col_name] = 0.0
    
        # add CI
        if ci_results:
            for col in ci_results.keys():
                if col in final_results.columns:
                    final_results[f'{col}_MC_mean'] = ci_results[col]['mean']
                    final_results[f'{col}_MC_std'] = ci_results[col]['std']
                    final_results[f'{col}_t_lower_{int(self.confidence_level_var.get()*100)}CI'] = ci_results[col]['lower_ci']
                    final_results[f'{col}_t_upper_{int(self.confidence_level_var.get()*100)}CI'] = ci_results[col]['upper_ci']
                    final_results[f'{col}_percentile_lower_{int(self.confidence_level_var.get()*100)}CI'] = ci_results[col]['percentile_lower']
                    final_results[f'{col}_percentile_upper_{int(self.confidence_level_var.get()*100)}CI'] = ci_results[col]['percentile_upper']
        for col in final_results.columns:
            for flux_var in flux_vars:
                if col.startswith(flux_var) and col.endswith(tuple(suffixes)):
                    final_results.loc[is_initial, col] = 0.0
        return final_results    
    

    
    def display_optimisation_results(self, optimisation_result):
        """Display optimisation results"""
        self.results_text.delete(1.0, tk.END)
        
        param_names = ['kLitter', 'LTurnoverR', 'BTurnoverR', 'CTurnoverR', 
                      'StTurnoverR', 'RhTurnoverR', 'RoTurnoverR', 'Rratio_Litter_layer']
        
        results_text = "PEMCAFE Model Optimisation Results\n"
        results_text += "=" * 50 + "\n\n"
        
        results_text += f"Optimisation Status: {'Success' if optimisation_result.success else 'Failed'}\n"
        results_text += f"Optimisation Method: {self.opt_method_var.get()}\n"
        results_text += f"Final Objective Value: {optimisation_result.fun:.6f}\n"
        results_text += f"Number of Iterations: {optimisation_result.nit if hasattr(optimisation_result, 'nit') else 'N/A'}\n\n"
        
        results_text += "Optimised Parameters:\n"
        results_text += "-" * 30 + "\n"
        for i, (name, value) in enumerate(zip(param_names, self.optimized_params)):
            results_text += f"{name:20}: {value:.6f}\n"
        
        if self.results is not None:
            results_text += "\n\nModel Results Summary:\n"
            results_text += "-" * 30 + "\n"
            
            key_vars = ['ANPP', 'BNPP', 'TNPP', 'NEP', 'GPP', 'AGC', 'BGC', 'TC']
            for var in key_vars:
                if var in self.results.columns:
                    mean_val = self.results[var].mean()
                    std_val = self.results[var].std()
                    results_text += f"{var:10}: Mean = {mean_val:8.3f}, Std = {std_val:8.3f}\n"
        
        self.results_text.insert(tk.END, results_text)
        
        # Switch to results tab
        self.notebook.select(4)
    
    def display_full_analysis_results(self, optimisation_result, ci_results):
        """Display full analysis results with confidence intervals"""
        self.results_text.delete(1.0, tk.END)
        
        param_names = ['kLitter', 'LTurnoverR', 'BTurnoverR', 'CTurnoverR', 
                      'StTurnoverR', 'RhTurnoverR', 'RoTurnoverR', 'Rratio_Litter_layer']
        
        results_text = "PEMCAFE Model Full Analysis Results\n"
        results_text += "=" * 60 + "\n\n"
        
        # Optimisation results
        results_text += "OPTIMISATION RESULTS:\n"
        results_text += f"Status: {'Success' if optimisation_result.success else 'Failed'}\n"
        results_text += f"Method: {self.opt_method_var.get()}\n"
        results_text += f"Final Objective Value: {optimisation_result.fun:.6f}\n\n"
        
        results_text += "Optimised Parameters:\n"
        for i, (name, value) in enumerate(zip(param_names, self.optimized_params)):
            results_text += f"  {name:20}: {value:.6f}\n"
        
        # Monte Carlo results
        results_text += f"\n\nMONTE CARLO SIMULATION RESULTS:\n"
        results_text += f"Number of Simulations: {self.n_simulations_var.get()}\n"
        results_text += f"Confidence Level: {self.confidence_level_var.get()*100:.0f}%\n\n"
        
        if ci_results:
            results_text += f"Summary of {self.confidence_level_var.get()*100:.0f}% Confidence Intervals for Key Variables:\n"
            results_text += "-" * 60 + "\n"
            
            key_vars = ['ANPP', 'BNPP', 'TNPP', 'NEP', 'GPP']
            for var in key_vars:
                if var in ci_results:
                    mean_val = np.mean(ci_results[var]['mean'])
                    mean_lower = np.mean(ci_results[var]['lower_ci'])
                    mean_upper = np.mean(ci_results[var]['upper_ci'])
                    results_text += f"{var:8}: {mean_val:8.3f} (CI: {mean_lower:8.3f} - {mean_upper:8.3f})\n"
        
        # Model settings summary
        results_text += f"\n\nMODEL SETTINGS:\n"
        results_text += f"Harvesting Bamboo Products (HBP): {self.hbp_var.get()}\n"
        results_text += f"BNPP Method: {'BGC + Dbelow' if self.bnpp_method_var.get() == 1 else 'BGC + Soil_AR'}\n"
        
        results_text += f"\n\nInput Data Summary:\n"
        results_text += f"Number of time points: {len(self.df) if self.df is not None else 'N/A'}\n"
        if self.df is not None:
            results_text += f"Data columns: {', '.join(self.df.columns.tolist())}\n"
        
        self.results_text.insert(tk.END, results_text)
        
        # Switch to results tab
        self.notebook.select(4)
    
    def export_results(self):
        """Export results to CSV file"""
        if self.results is None:
            messagebox.showwarning("Warning", "No results to export. Please run the model first.")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Results",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                self.results.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Results exported to {filename}")
                self.status_var.set(f"Results exported to {os.path.basename(filename)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")

def main():
    root = tk.Tk()
    app = PEMCAFEModelGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
