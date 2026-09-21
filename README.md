# AI-Powered Smart Classroom Occupancy & Resource Planning

> **An Intelligent Data Analytics and Machine Learning System for Classroom Occupancy Analysis, Prediction, Utilization Monitoring, and Resource Planning**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange.svg)](https://scikit-learn.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-brightgreen.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 👨‍💻 Author Information

- **Author**: Kanda Saptha Sri Vardhan
- **Email**: [vardhankanda13@gmail.com](mailto:vardhankanda13@gmail.com)
- **Project**: AI-Powered Smart Classroom Occupancy & Resource Planning

---

## 📖 Overview

The **AI-Powered Smart Classroom Occupancy & Resource Planning Platform** is an enterprise-grade, privacy-preserving IoT analytics and predictive intelligence solution. By ingesting multi-modal non-intrusive sensor streams (temperature gradients, ambient light levels, acoustic sound pressure, $\text{CO}_2$ concentration dynamics, and passive infrared motion detection), the platform provides real-time occupancy estimation, automated energy conservation strategies, and data-driven facility resource scheduling.

---

## 🎯 Problem Statement

Higher education campuses and commercial institutions incur substantial overhead costs maintaining climate control (HVAC) and lighting in unoccupied or underutilized lecture halls. Conventional scheduling relies on static timetables that frequently diverge from real-world attendance. Traditional vision-based occupancy monitoring introduces substantial privacy concerns and network bandwidth bottlenecks. 

**Solution**: This system provides high-fidelity, non-intrusive occupancy inference using environmental telemetry, enabling demand-controlled ventilation (DCV), daylight harvesting, and automated facility dispatching.

---

## 📌 Dataset Source & Attribution

### Dataset Source
- **Dataset**: Room Occupancy Estimation
- **Source**: [https://www.kaggle.com/datasets/ruchikakumbhar/room-occupancy-estimation](https://www.kaggle.com/datasets/ruchikakumbhar/room-occupancy-estimation)
- **Dataset Used**: `dataset/room occupancy.csv`

### Dataset Statistics
- **Total Records (Rows)**: `10,129`
- **Telemetry Channels (Columns)**: `19` raw features (`31` features post-engineering)
- **Target Variable**: `Room_Occupancy_Count` (Ground truth: `0`, `1`, `2`, `3` occupants) / `Is_Occupied` (`0` = Vacant, `1` = Occupied)
- **Date Range**: `2017-12-22 10:49:41` to `2018-01-11 09:00:09` (`7` unique monitoring days)
- **Data Quality Score**: `100.0 / 100` (`0` nulls, `0` duplicate rows)

---

## 🗄️ Dataset Architecture & Data Dictionary

| Field Name | Data Type | Physical Unit | Description |
| :--- | :--- | :--- | :--- |
| `Date` | `object` | `DD-MM-YYYY` | Calendar date of telemetry recording |
| `Time` | `object` | `HH:MM:SS` | Synchronized time of sensor capture |
| `S1_Temp` – `S4_Temp` | `float64` | Celsius (°C) | Micro-climate temperature across room zones |
| `S1_Light` – `S4_Light` | `int64` | Lux (lx) | Illuminance capturing ambient daylight and luminaires |
| `S1_Sound` – `S4_Sound` | `float64` | Volts (V) | Amplified acoustic pressure measuring ambient noise |
| `S5_CO2` | `int64` | Parts Per Million (PPM) | Carbon dioxide concentration from air quality sensor |
| `S5_CO2_Slope` | `float64` | PPM / min | First derivative (rate of change) in CO2 concentration |
| `PIR1`, `PIR2` | `int64` | Binary (0 / 1) | Passive infrared motion detector activations |
| `Room_Occupancy_Count` | `int64` | Count (0–3) | Ground truth count of occupants in room |

---

## 🔄 Data Processing & Engineering Pipeline

1. **Ingestion & Validation**: Safe loading preserving raw data in memory (`raw_df` vs `clean_df`).
2. **Chronological Sorting**: Timestamps parsed using `dayfirst=True` format and sorted chronologically.
3. **Target Definition**: Binary state `Is_Occupied` ($1$ if `Room_Occupancy_Count` > 0, else $0$).
4. **Temporal Extraction**: Derived `Hour`, `Day_of_Week`, `Day_Name`, `Month_Name`, `Is_Weekend`, and categorical `Time_Period` (`Morning`, `Midday/Class Peak`, `Afternoon`, `Evening`, `Night`).
5. **Target Leakage Prevention**: Identifiers (`Date`, `Time`, `DateTime`) and target variables are strictly excluded from predictive model training.

---

## 🤖 Machine Learning Benchmarks

Models are evaluated using an **80/20 chronological holdout split** (8,103 training samples $\rightarrow$ 2,026 holdout test samples) to strictly prevent future data leakage.

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Regularized Logistic Regression** | **99.85%** | **99.64%** | **99.27%** | **99.45%** | **1.0000** |
| **Hist Gradient Boosting** | **99.21%** | **99.62%** | **94.55%** | **97.01%** | **0.9995** |
| **Random Forest Classifier** | **96.69%** | **100.00%** | **75.64%** | **86.13%** | **0.9999** |

---

## 🌲 Feature Importance Ranking (Random Forest)

The relative importance of environmental sensor features for predicting classroom occupancy:

1. **`S1_Light`**: `28.70%`
2. **`S2_Light`**: `23.69%`
3. **`S1_Sound`**: `13.13%`
4. **`S5_CO2_Slope`**: `9.44%`
5. **`S2_Sound`**: `8.80%`
6. **`S3_Sound`**: `6.30%`
7. **`S5_CO2`**: `2.32%`
8. **`S3_Light`**: `1.93%`
9. **`S2_Temp`**: `1.83%`
10. **`S4_Temp`**: `1.35%`

---

## 📱 Dashboard Modules

The application provides 13 dedicated analytics sections accessible via the sidebar:

1. **📊 Executive Dashboard**: High-level KPIs, 24-hr occupancy curves, day-of-week heatmaps, and dynamic AI analytical summaries.
2. **🗃️ Dataset Overview**: Schema inspection, column statistics, memory profiling, and CSV export.
3. **🔍 Data Quality**: Data Quality Index ($100/100$), missingness audit, duplicate checks, and IQR outlier detection.
4. **🧹 Data Cleaning**: Raw vs Cleaned audit comparison and schema transformation logs.
5. **⚙️ Feature Engineering**: Temporal decompositions and time-period utilization breakdowns.
6. **📈 Occupancy Analytics**: Target frequency histograms, weekday curves, and hourly occupancy boxplots.
7. **🌡️ Sensor Analytics**: Full correlation heatmap, pairwise scatter clustering, and occupancy-conditioned sensor distributions.
8. **💡 Utilization Intelligence**: Data-driven Classroom Utilization Score ($18.77\%$), idle hours, and capacity stress profiles.
9. **🤖 AI Prediction**: Live interactive simulation interface with parameter sliders and confidence gauges.
10. **🎯 Model Evaluation**: Chronological evaluation benchmarks, confusion matrices, and feature importance bar charts.
11. **🏢 Resource Planning**: HVAC dynamic setback recommendations, daylight harvesting automation, and custodial dispatch advice.
12. **📋 Insights & Recommendations**: Data-driven observation-insight-implication framework.
13. **ℹ️ About Project**: Architecture, methodology, technology stack, and Kaggle attribution.

---

## 💡 Key Analytical Findings & Resource Planning

1. **Classroom Utilization Rate**: The empirical utilization rate is **$18.77\%$** ($1,901$ occupied intervals out of $10,129$), with peak occupancy occurring during mid-day lecture hours ($10:00 - 14:00$).
2. **Optical & Acoustic Dominance**: Illuminance and sound sensors exhibit the highest information gain, capturing immediate human entry before thermal or gas changes occur.
3. **CO2 Rate of Change Advantage**: $\text{S5\_CO2\_Slope}$ (rate of change) detects occupancy faster than raw $\text{CO}_2$ PPM concentration, which suffers from room volume dilution lag.
4. **Energy Optimization Potential**: With an **$81.23\%$** vacancy rate, automated HVAC setback schedules and daylight harvesting can reduce standby facility energy consumption by an estimated **$30–45\%$**.

---

## 🏗️ Project Structure

```text
AI-Powered Smart Classroom Occupancy & Resource Planning/
│
├── dataset/
│   └── room occupancy.csv                                                  # 10,129-row multi-modal IoT sensor dataset
│
├── KandaSapthaSriVardhan_AIPoweredSmartClassroomOccupancyResourcePlanning.py # Complete single-file Streamlit application
├── requirements.txt                                                         # Pinned core dependencies
├── README.md                                                                # Comprehensive project documentation
├── LICENSE                                                                  # MIT License
├── KandaSapthaSriVardhan_AIPoweredSmartClassroomOccupancyResourcePlanning_ProjectReport.docx # Submission project report
└── .gitignore                                                               # Standard git ignore configuration
```

---

## 🚀 Installation & Quick Start

### 1. Set Up Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run KandaSapthaSriVardhan_AIPoweredSmartClassroomOccupancyResourcePlanning.py
```

The web dashboard will open automatically at `http://localhost:8501`.

---

## 📜 Ethical & Privacy Considerations

- **Privacy by Design**: The system exclusively processes non-visual, non-acoustic-recording telemetry (ambient lux, acoustic voltage levels, CO2, temperature). No personally identifiable information (PII) or audio feeds are captured.
- **Safety Overrides**: Recommended HVAC setbacks maintain baseline ventilation rates adhering to ASHRAE 62.1 indoor air quality standards.

---

## 📄 License & Attribution

- **License**: [MIT License](LICENSE) — Copyright (c) 2026 Kanda Saptha Sri Vardhan
- **Dataset Source**: [Room Occupancy Estimation on Kaggle](https://www.kaggle.com/datasets/ruchikakumbhar/room-occupancy-estimation) by Ruchika Kumbhar.
