# PEMCAFE (Process-based Ecosystem Model for Carbon Assessment in Forest Ecosystems)

## English Version

### Overview
PEMCAFE (version 0.9, released October 10, 2024) is a process-based ecosystem model designed for carbon assessment in forest ecosystems. The model calculates various carbon-related metrics including:

- Above-ground Net Primary Production (ANPP)
- Below-ground Net Primary Production (BNPP)
- Total Net Primary Production (TNPP)
- Net Ecosystem Production (NEP)
- Gross Primary Production (GPP)

### Key Features
- Comprehensive carbon pool calculations
- Two methods for BNPP estimation
- Automated parameter optimization
- Iterative convergence mechanism
- Optional harvested bamboo products consideration

### Requirements
- Python 3.x
- Required packages: pandas, numpy, scipy
- Input CSV file with forest measurement data

### Usage
1. Prepare your input data in CSV format
2. Set the appropriate parameters in the configuration section
3. Choose BNPP calculation method (BNG + Dbelow or BNG + Soil_AR)
4. Run the script to obtain optimized results

---

## 繁體中文版本

### 概述
PEMCAFE（版本0.9，2024年10月10日發布）是一個針對森林生態系統進行碳評估的過程型生態系統模型。該模型計算多項碳相關指標，包括：

- 地上部淨初級生產力（ANPP）
- 地下部淨初級生產力（BNPP）
- 總淨初級生產力（TNPP）
- 淨生態系統生產力（NEP）
- 總初級生產力（GPP）

### 主要特點
- 全面的碳庫計算
- 兩種BNPP估算方法
- 自動參數優化
- 迭代收斂機制
- 可選擇性考慮竹產品收穫

### 系統需求
- Python 3.x
- 必要套件：pandas, numpy, scipy
- 含森林測量數據的CSV輸入檔案

### 使用方法
1. 準備CSV格式的輸入數據
2. 在配置區段設定適當參數
3. 選擇BNPP計算方法（BNG + Dbelow 或 BNG + Soil_AR）
4. 執行腳本以獲得優化結果

---

## 日本語版

### 概要
PEMCAFE（バージョン0.9、2024年10月10日リリース）は、森林生態系における炭素評価のためのプロセスベースの生態系モデルです。このモデルは以下の炭素関連指標を計算します：

- 地上部純一次生産量（ANPP）
- 地下部純一次生産量（BNPP）
- 総純一次生産量（TNPP）
- 生態系純生産量（NEP）
- 総一次生産量（GPP）

### 主な特徴
- 包括的な炭素プール計算
- 2種類のBNPP推定方法
- パラメータの自動最適化
- 反復収束メカニズム
- 竹製品収穫の選択的考慮

### 必要条件
- Python 3.x
- 必要なパッケージ：pandas, numpy, scipy
- 森林測定データを含むCSV入力ファイル

### 使用方法
1. CSV形式で入力データを準備
2. 設定セクションで適切なパラメータを設定
3. BNPP計算方法を選択（BNG + Dbelow または BNG + Soil_AR）
4. スクリプトを実行して最適化された結果を取得
