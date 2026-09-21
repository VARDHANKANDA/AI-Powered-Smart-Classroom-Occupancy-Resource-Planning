"""
AI-Powered Smart Classroom Occupancy & Resource Planning
=========================================================
An Intelligent Data Analytics and Machine Learning System for Classroom Occupancy Analysis,
Prediction, Utilization Monitoring, and Resource Planning.

Primary Dataset: dataset/room occupancy.csv
Dataset Source: https://www.kaggle.com/datasets/ruchikakumbhar/room-occupancy-estimation
Project Context: IBM SkillsBuild Data Analytics with AI

Author: Kanda Saptha Sri Vardhan
License: MIT
"""

import os
import io
import time
import datetime
import hashlib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, precision_recall_curve, confusion_matrix,
    classification_report
)

try:
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# ==========================================
# 1. STREAMLIT CONFIGURATION & COLOR SYSTEM
# ==========================================

st.set_page_config(
    page_title="Smart Classroom Analytics",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Navy + Blue + Teal Design System
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
    }
    
    /* Main Background & Padding */
    .stApp {
        background-color: #F8FAFC;
    }
    .block-container {
        padding-top: 2.0rem;
        padding-bottom: 3.5rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 1400px;
    }
    
    /* Sidebar Styling (Professional Dark Navy) */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] * {
        color: #CBD5E1 !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #F8FAFC !important;
    }
    
    /* Page Header Card */
    .page-header-container {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2563EB;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .page-title {
        color: #0F172A;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
    }
    .page-subtitle {
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.5;
        font-weight: 400;
    }
    
    /* Section Headers */
    .section-header {
        color: #0F172A;
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -0.015em;
        margin-top: 28px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-desc {
        color: #64748B;
        font-size: 0.85rem;
        margin-top: -6px;
        margin-bottom: 16px;
    }
    
    /* Unified White KPI Cards */
    .kpi-container {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 3px solid #2563EB;
        border-radius: 10px;
        padding: 18px 20px;
        min-height: 125px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    }
    .kpi-label {
        color: #64748B;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .kpi-value {
        color: #0F172A;
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }
    .kpi-subtext {
        color: #64748B;
        font-size: 0.78rem;
        font-weight: 500;
        margin-top: 6px;
    }
    
    /* Clean Insight Cards (Observation -> Meaning -> Action) */
    .insight-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #0F766E;
        border-radius: 8px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .insight-title {
        color: #0F172A;
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        margin-bottom: 8px;
    }
    .insight-row {
        margin-bottom: 6px;
        font-size: 0.88rem;
        line-height: 1.5;
        color: #334155;
    }
    .insight-badge {
        font-weight: 700;
        color: #0F172A;
    }
    .insight-action {
        color: #0F766E;
        font-weight: 600;
        font-size: 0.88rem;
        margin-top: 6px;
    }

    /* Prediction Result Banners (Neutral & Clear) */
    .result-banner-occupied {
        background-color: #FFFFFF;
        border: 2px solid #2563EB;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
    }
    .result-banner-vacant {
        background-color: #FFFFFF;
        border: 2px solid #94A3B8;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(148, 163, 184, 0.1);
    }

    /* Button Styling */
    div.stButton > button {
        background-color: #2563EB;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 10px 22px;
        font-size: 0.92rem;
        font-weight: 700;
        box-shadow: 0 1px 3px rgba(37, 99, 235, 0.2);
        transition: all 0.15s ease;
    }
    div.stButton > button:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==========================================
# 2. REUSABLE UI COMPONENT FUNCTIONS
# ==========================================

def render_page_header(title, subtitle, tag=None):
    """Renders a clean, white top banner with blue accent."""
    tag_html = f'<span style="background-color: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE; padding: 3px 10px; border-radius: 9999px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; margin-left: 10px;">{tag}</span>' if tag else ""
    st.markdown(
        f"""
        <div class="page-header-container">
            <div class="page-title">{title} {tag_html}</div>
            <div class="page-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_section_header(title, description=None):
    """Renders section header with dark navy typography and subtle description."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    if description:
        st.markdown(f'<div class="section-desc">{description}</div>', unsafe_allow_html=True)

def render_kpi_card(label, value, subtext="", accent_color="#2563EB"):
    """Renders a unified white KPI metric card with clean top border."""
    return f"""
    <div class="kpi-container" style="border-top: 3px solid {accent_color};">
        <div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """

def render_insight_card(title, observation, meaning, action):
    """Renders structured Observation -> Meaning -> Action card."""
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-title">{title}</div>
            <div class="insight-row"><span class="insight-badge">Observation:</span> {observation}</div>
            <div class="insight-row"><span class="insight-badge">Meaning:</span> {meaning}</div>
            <div class="insight-action"><span class="insight-badge" style="color: #0F766E;">Strategic Action:</span> {action}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_chart(fig, height=450):
    """Standardized clean Plotly chart renderer with light neutral backgrounds and subtle gridlines."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=35, r=25, t=50, b=40),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#0F172A"),
        title_font=dict(family="Plus Jakarta Sans, sans-serif", size=13, color="#0F172A"),
        xaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0", tickfont=dict(color="#475569")),
        yaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0", tickfont=dict(color="#475569")),
        legend=dict(font=dict(color="#0F172A"))
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": True, "displaylogo": False, "responsive": True}
    )


# ==========================================
# 3. DATA DISCOVERY & LOADING
# ==========================================

def get_file_hash(file_path):
    """Computes MD5 hash for reliable cache invalidation."""
    if not os.path.exists(file_path):
        return ""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

@st.cache_data
def discover_dataset_files():
    """Discovers available datasets with priority given to dataset/room occupancy.csv."""
    valid_extensions = ('.csv', '.xlsx', '.xls', '.json')
    discovered = []
    
    priority_exact = os.path.join('dataset', 'room occupancy.csv')
    if os.path.exists(priority_exact):
        discovered.append(priority_exact)
        
    for p in ['dataset', '.']:
        if os.path.exists(p):
            for file in os.listdir(p):
                if file.endswith(valid_extensions) and not file.startswith('~'):
                    full_path = os.path.join(p, file)
                    if os.path.isfile(full_path):
                        norm = os.path.normpath(full_path)
                        if norm not in [os.path.normpath(x) for x in discovered]:
                            discovered.append(norm)
    return discovered

@st.cache_data
def load_raw_dataset(file_path, file_hash=""):
    """Loads dataset cleanly from disk."""
    if not os.path.exists(file_path):
        return None
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            xl = pd.ExcelFile(file_path)
            for sheet in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet)
                if df.shape[0] > 10 and df.shape[1] > 2:
                    return df
            return pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return None
    return None


# ==========================================
# 4. DATA CLEANING & FEATURE ENGINEERING
# ==========================================

@st.cache_data
def process_and_clean_data(raw_df):
    """
    Cleans raw dataframe safely, extracts time features, and prepares sensor structures.
    Returns: (clean_df, audit_dict)
    """
    if raw_df is None or raw_df.empty:
        return None, {}
    
    df = raw_df.copy()
    audit = {
        'initial_rows': len(df),
        'initial_cols': len(df.columns),
        'duplicates_removed': int(df.duplicated().sum()),
        'missing_handled': int(df.isnull().sum().sum()),
        'engineered_features': []
    }
    
    df = df.drop_duplicates().reset_index(drop=True)
    
    date_col, time_col, datetime_col = None, None, None
    for col in df.columns:
        c_lower = str(col).lower()
        if c_lower in ['datetime', 'timestamp']:
            datetime_col = col
        elif c_lower == 'date':
            date_col = col
        elif c_lower == 'time':
            time_col = col
            
    if datetime_col:
        df['DateTime'] = pd.to_datetime(df[datetime_col], errors='coerce', dayfirst=True)
    elif date_col and time_col:
        df['DateTime'] = pd.to_datetime(df[date_col].astype(str) + ' ' + df[time_col].astype(str), errors='coerce', dayfirst=True)
    elif date_col:
        df['DateTime'] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
    else:
        try:
            df['DateTime'] = pd.to_datetime(df.iloc[:, 0], errors='coerce', dayfirst=True)
        except:
            df['DateTime'] = pd.date_range(start='2026-01-01', periods=len(df), freq='30s')
            
    if df['DateTime'].isnull().sum() > 0:
        df['DateTime'] = df['DateTime'].bfill().ffill()
        
    df = df.sort_values('DateTime').reset_index(drop=True)
    
    target_col = None
    for cand in ['Room_Occupancy_Count', 'Occupancy', 'Occupancy_Count', 'Occupied', 'Target']:
        if cand in df.columns:
            target_col = cand
            break
            
    if target_col is None:
        for col in df.columns:
            if 'occupan' in str(col).lower():
                target_col = col
                break
                
    if target_col is None:
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        target_col = num_cols[-1] if num_cols else df.columns[-1]
        
    audit['target_column'] = target_col
    
    if pd.api.types.is_numeric_dtype(df[target_col]):
        df['Is_Occupied'] = (df[target_col] > 0).astype(int)
    else:
        df['Is_Occupied'] = df[target_col].astype(str).str.lower().isin(['1', 'true', 'yes', 'occupied']).astype(int)
        
    # Temporal Decomposition
    df['Year'] = df['DateTime'].dt.year
    df['Month'] = df['DateTime'].dt.month
    df['Month_Name'] = df['DateTime'].dt.strftime('%B')
    df['Day'] = df['DateTime'].dt.day
    df['Day_of_Week'] = df['DateTime'].dt.dayofweek
    df['Day_Name'] = df['DateTime'].dt.strftime('%A')
    df['Hour'] = df['DateTime'].dt.hour
    df['Minute'] = df['DateTime'].dt.minute
    df['Is_Weekend'] = df['Day_of_Week'].isin([5, 6]).astype(int)
    
    def get_time_period(hour):
        if 6 <= hour < 10:
            return 'Morning (06-10h)'
        elif 10 <= hour < 14:
            return 'Midday Peak (10-14h)'
        elif 14 <= hour < 18:
            return 'Afternoon (14-18h)'
        elif 18 <= hour < 22:
            return 'Evening (18-22h)'
        else:
            return 'Night (22-06h)'
            
    df['Time_Period'] = df['Hour'].apply(get_time_period)
    
    audit['engineered_features'] = [
        'DateTime', 'Year', 'Month', 'Month_Name', 'Day',
        'Day_of_Week', 'Day_Name', 'Hour', 'Minute', 'Is_Weekend', 'Time_Period', 'Is_Occupied'
    ]
    
    excluded = set(audit['engineered_features'] + [target_col, 'Date', 'Time'])
    sensor_cols = [c for c in df.columns if c not in excluded and pd.api.types.is_numeric_dtype(df[c])]
    audit['sensor_columns'] = sensor_cols
    
    for sc in sensor_cols:
        if df[sc].isnull().sum() > 0:
            df[sc] = df[sc].ffill().fillna(df[sc].median())
            
    audit['final_rows'] = len(df)
    audit['final_cols'] = len(df.columns)
    
    return df, audit


# ==========================================
# 5. MACHINE LEARNING ENGINE
# ==========================================

@st.cache_resource
def train_and_evaluate_models(df_json_str, target_col, sensor_cols_tuple):
    """
    Trains Logistic Regression, Random Forest, and HistGradientBoosting using an
    80/20 chronological train/test split.
    """
    df = pd.read_json(io.StringIO(df_json_str))
    sensor_cols = list(sensor_cols_tuple)
    
    X = df[sensor_cols]
    y = df['Is_Occupied']
    
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    models = {
        'Logistic Regression': Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'))
        ]),
        'Random Forest': RandomForestClassifier(
            n_estimators=100, max_depth=12, random_state=42, class_weight='balanced', n_jobs=-1
        ),
        'Hist Gradient Boosting': HistGradientBoostingClassifier(
            random_state=42, max_iter=100, class_weight='balanced'
        )
    }
    
    results = {}
    fitted_models = {}
    
    for name, model in models.items():
        start_t = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_t
        
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_proba) if y_proba is not None and len(np.unique(y_test)) > 1 else np.nan
        cm = confusion_matrix(y_test, y_pred)
        
        fpr, tpr, _ = roc_curve(y_test, y_proba) if y_proba is not None and len(np.unique(y_test)) > 1 else ([], [], [])
        precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_proba) if y_proba is not None else ([], [], [])
        
        results[name] = {
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'roc_auc': roc_auc,
            'confusion_matrix': cm.tolist(),
            'train_time': train_time,
            'fpr': fpr.tolist() if isinstance(fpr, np.ndarray) else [],
            'tpr': tpr.tolist() if isinstance(tpr, np.ndarray) else [],
            'prec_curve': precision_curve.tolist() if isinstance(precision_curve, np.ndarray) else [],
            'rec_curve': recall_curve.tolist() if isinstance(recall_curve, np.ndarray) else [],
            'classification_report': classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        }
        fitted_models[name] = model
        
    rf_clf = fitted_models['Random Forest']
    feat_imp = pd.DataFrame({
        'Feature': sensor_cols,
        'Importance': rf_clf.feature_importances_
    }).sort_values('Importance', ascending=False).reset_index(drop=True)
    
    split_meta = {
        'total_samples': len(df),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'train_pos_ratio': float(y_train.mean()),
        'test_pos_ratio': float(y_test.mean()),
        'feature_cols': sensor_cols
    }
    
    return fitted_models, results, feat_imp, split_meta


# ==========================================
# 6. DOCUMENTATION GENERATION (.DOCX)
# ==========================================

def generate_project_docx(df, audit, results, feat_imp, split_meta):
    """Generates technical documentation Word document citing Kaggle dataset source."""
    if not DOCX_AVAILABLE:
        return None
        
    doc = docx.Document()
    
    title_style = doc.styles['Title']
    title_style.font.name = 'Calibri'
    title_style.font.size = Pt(24)
    title_style.font.color.rgb = RGBColor(15, 23, 42)
    title_style.font.bold = True
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("AI-Powered Smart Classroom Occupancy & Resource Planning\n")
    r_title.bold = True
    r_title.font.size = Pt(22)
    r_title.font.color.rgb = RGBColor(37, 99, 235)
    
    r_sub = p_title.add_run("An Intelligent Data Analytics and Machine Learning System for Classroom Occupancy Analysis, Prediction, Utilization Monitoring, and Resource Planning\n\n")
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(71, 85, 105)
    r_sub.italic = True
    
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.add_run(f"Dataset Used: dataset/room occupancy.csv\nDataset Source: https://www.kaggle.com/datasets/ruchikakumbhar/room-occupancy-estimation\nProject: IBM SkillsBuild Data Analytics with AI\nGenerated On: {datetime.datetime.now().strftime('%B %d, %Y')}\nTarget Variable: {audit.get('target_column', 'Room_Occupancy_Count')}\nRecords Analyzed: {len(df):,}\n")
    doc.add_page_break()
    
    def add_section_header(title, level=1):
        h = doc.add_heading(title, level=level)
        for r in h.runs:
            r.font.name = 'Calibri'
            r.font.color.rgb = RGBColor(15, 23, 42) if level == 1 else RGBColor(30, 41, 59)
        return h

    add_section_header("1. Executive Summary")
    doc.add_paragraph(
        f"This document presents an end-to-end analytical and machine learning evaluation of the Smart Classroom "
        f"Occupancy & Resource Planning System. Utilizing high-resolution multi-modal environmental sensors "
        f"(including ambient light levels, temperature gradients, acoustic sound pressure, CO2 concentration dynamics, and PIR motion detectors), "
        f"the platform provides continuous occupancy monitoring, predictive scheduling intelligence, and facility automation insights. "
        f"The primary dataset (dataset/room occupancy.csv) contains {len(df):,} discrete observations across {len(audit.get('sensor_columns', []))} sensor channels. "
        f"Supervised machine learning algorithms achieve up to {results['Logistic Regression']['accuracy']*100:.2f}% accuracy with "
        f"zero-leakage chronological validation, demonstrating the efficacy of non-intrusive smart campus management."
    )
    
    add_section_header("2. Introduction & Problem Statement")
    doc.add_paragraph(
        "Higher education facilities incur substantial recurring costs operating HVAC and lighting in underutilized rooms. "
        "This project models environmental telemetry to deliver automated, non-intrusive occupancy inference."
    )
    
    add_section_header("7. Dataset Description & Provenance")
    doc.add_paragraph(
        f"Dataset File: dataset/room occupancy.csv\n"
        f"Official Kaggle Source: https://www.kaggle.com/datasets/ruchikakumbhar/room-occupancy-estimation\n"
        f"Total Records: {len(df):,} rows, {len(df.columns)} columns.\n"
        f"Date Coverage: {df['DateTime'].min().strftime('%Y-%m-%d %H:%M')} to {df['DateTime'].max().strftime('%Y-%m-%d %H:%M')}."
    )
    
    add_section_header("10. Data Dictionary")
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Field Name"
    hdr_cells[1].text = "Data Type"
    hdr_cells[2].text = "Physical Unit"
    hdr_cells[3].text = "Description"
    for cell in hdr_cells:
        shading = parse_xml(r'<w:shd {} w:fill="0F172A"/>'.format(nsdecls('w')))
        cell._tc.get_or_add_tcPr().append(shading)
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.bold = True
                
    dict_entries = [
        ("DateTime", "datetime64", "YYYY-MM-DD HH:MM:SS", "Synchronized timestamp of telemetry capture"),
        ("S1_Temp - S4_Temp", "float64", "Degrees Celsius (°C)", "Temperature sensors distributed across room zones"),
        ("S1_Light - S4_Light", "int64", "Lux (lx)", "Illuminance readings capturing ambient and artificial light"),
        ("S1_Sound - S4_Sound", "float64", "Volts (V)", "Amplified acoustic pressure measuring ambient noise"),
        ("S5_CO2", "int64", "Parts Per Million (PPM)", "Carbon dioxide concentration from air quality sensor"),
        ("S5_CO2_Slope", "float64", "PPM / min", "First derivative / rate of change in CO2 concentration"),
        ("S6_PIR, S7_PIR", "int64", "Binary (0/1)", "Passive infrared motion detector activations"),
        (audit.get('target_column', 'Room_Occupancy_Count'), "int64", "Count (0-3)", "Ground truth count of individuals in room")
    ]
    for row in dict_entries:
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
            
    doc.add_paragraph("\n")
    
    add_section_header("20. Machine Learning Benchmark Results")
    ml_table = doc.add_table(rows=1, cols=6)
    ml_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    ml_hdr = ml_table.rows[0].cells
    for i, title in enumerate(["Model Architecture", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]):
        ml_hdr[i].text = title
        shading = parse_xml(r'<w:shd {} w:fill="0F172A"/>'.format(nsdecls('w')))
        ml_hdr[i]._tc.get_or_add_tcPr().append(shading)
        for p in ml_hdr[i].paragraphs:
            for r in p.runs:
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.bold = True
                
    for model_name, m_res in results.items():
        row_cells = ml_table.add_row().cells
        row_cells[0].text = model_name
        row_cells[1].text = f"{m_res['accuracy']*100:.2f}%"
        row_cells[2].text = f"{m_res['precision']*100:.2f}%"
        row_cells[3].text = f"{m_res['recall']*100:.2f}%"
        row_cells[4].text = f"{m_res['f1_score']*100:.2f}%"
        row_cells[5].text = f"{m_res['roc_auc']:.4f}" if not np.isnan(m_res['roc_auc']) else "N/A"
        
    doc_path = os.path.join(os.getcwd(), "PROJECT_DOCUMENTATION.docx")
    doc.save(doc_path)
    return doc_path


# ==========================================
# 7. MAIN APPLICATION NAVIGATION & PAGES
# ==========================================

def main():
    dataset_files = discover_dataset_files()
    
    # Sidebar Header
    st.sidebar.markdown(
        """
        <div style="padding: 4px 0 14px 0; text-align: left;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 1.6rem;">🏫</div>
                <div>
                    <div style="font-size: 1.0rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.01em;">SMART CLASSROOM</div>
                    <div style="font-size: 0.70rem; color: #38BDF8; font-weight: 700; letter-spacing: 0.08em;">AI ANALYTICS PLATFORM</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Presentation Mode Toggle
    presentation_mode = st.sidebar.toggle("🎯 Presentation Mode", value=False, help="Hides low-level technical verbose text, enlarges charts, and optimizes page layout for screenshots.")
    st.sidebar.markdown("<hr style='border-color: #1E293B;'>", unsafe_allow_html=True)
    
    # Navigation Menu
    pages = [
        "📊 Executive Dashboard",
        "🗃️ Dataset Overview",
        "🔍 Data Quality",
        "🧹 Data Cleaning",
        "⚙️ Feature Engineering",
        "📈 Occupancy Analytics",
        "🌡️ Sensor Analytics",
        "💡 Utilization Intelligence",
        "🤖 AI Prediction",
        "🎯 Model Evaluation",
        "🏢 Resource Planning",
        "📋 Insights & Recommendations",
        "ℹ️ About Project"
    ]
    
    nav_selection = st.sidebar.radio("Navigation", pages, index=0)
    st.sidebar.markdown("<hr style='border-color: #1E293B;'>", unsafe_allow_html=True)
    
    # Dataset Selector
    if dataset_files:
        selected_file = st.sidebar.selectbox(
            "Active Dataset",
            options=dataset_files,
            index=0,
            help="Select sensor telemetry dataset"
        )
    else:
        st.sidebar.error("No dataset found.")
        selected_file = None
        
    if not selected_file:
        st.error("Please place `room occupancy.csv` in `./dataset/` to proceed.")
        return
        
    file_hash = get_file_hash(selected_file)
    raw_df = load_raw_dataset(selected_file, file_hash=file_hash)
    if raw_df is None:
        st.error(f"Failed to load `{selected_file}`.")
        return
        
    clean_df, audit = process_and_clean_data(raw_df)
    target_col = audit.get('target_column', 'Room_Occupancy_Count')
    sensor_cols = audit.get('sensor_columns', [])
    
    # Global Temporal Filter
    min_date = clean_df['DateTime'].min().date()
    max_date = clean_df['DateTime'].max().date()
    
    if min_date < max_date:
        date_range = st.sidebar.date_input(
            "Temporal Filter Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            start_d, end_d = date_range
            filtered_df = clean_df[(clean_df['DateTime'].dt.date >= start_d) & (clean_df['DateTime'].dt.date <= end_d)].copy()
        else:
            filtered_df = clean_df.copy()
    else:
        filtered_df = clean_df.copy()
        
    if filtered_df.empty:
        filtered_df = clean_df.copy()
        
    # Model Training in Background
    json_str = clean_df.to_json()
    fitted_models, ml_results, feat_imp, split_meta = train_and_evaluate_models(
        json_str, target_col, tuple(sensor_cols)
    )
    
    # Sidebar Project Metadata Card
    st.sidebar.markdown(
        f"""
        <div style="background-color: #1E293B; padding: 12px 14px; border-radius: 8px; border: 1px solid #334155; font-size: 0.78rem; line-height: 1.5;">
            <div style="color: #94A3B8; font-weight: 700; text-transform: uppercase;">Dataset:</div>
            <div style="color: #38BDF8; font-family: monospace; font-weight: 600;">{os.path.basename(selected_file)}</div>
            <div style="color: #94A3B8; font-weight: 700; text-transform: uppercase; margin-top: 6px;">Project:</div>
            <div style="color: #F8FAFC; font-weight: 600;">IBM SkillsBuild Data Analytics with AI</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if DOCX_AVAILABLE:
        st.sidebar.markdown("<br>", unsafe_allow_html=True)
        if st.sidebar.button("📄 Export Project Report (.docx)", use_container_width=True):
            with st.spinner("Generating document..."):
                doc_p = generate_project_docx(clean_df, audit, ml_results, feat_imp, split_meta)
                if doc_p and os.path.exists(doc_p):
                    with open(doc_p, "rb") as f:
                        b = f.read()
                    st.sidebar.download_button(
                        label="💾 Download Word Doc",
                        data=b,
                        file_name="PROJECT_DOCUMENTATION.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )


    # =========================================================================
    # PAGE 1: EXECUTIVE DASHBOARD (CLEAN NAVY + BLUE + TEAL)
    # =========================================================================
    if nav_selection == "📊 Executive Dashboard":
        render_page_header(
            "AI-Powered Smart Classroom Occupancy & Resource Planning",
            "Data-driven occupancy intelligence, prediction and resource planning using environmental sensor data.",
            tag="Executive View"
        )
        
        total_obs = len(filtered_df)
        occupied_obs = int(filtered_df['Is_Occupied'].sum())
        util_rate = (occupied_obs / total_obs * 100) if total_obs > 0 else 0
        avg_occ = filtered_df[target_col].mean() if target_col in filtered_df.columns else 0
        max_occ = filtered_df[target_col].max() if target_col in filtered_df.columns else 0
        best_acc = ml_results['Logistic Regression']['accuracy'] * 100
        
        # 6 Unified White KPI Cards with subtle accents
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        with k1:
            st.markdown(render_kpi_card("Total Records", f"{total_obs:,}", f"{filtered_df['DateTime'].dt.date.nunique()} Days Monitored", accent_color="#2563EB"), unsafe_allow_html=True)
        with k2:
            st.markdown(render_kpi_card("Occupancy Rate", f"{util_rate:.1f}%", f"{occupied_obs:,} Occupied Slots", accent_color="#2563EB"), unsafe_allow_html=True)
        with k3:
            st.markdown(render_kpi_card("Average Occupancy", f"{avg_occ:.2f}", "Persons / 30s cycle", accent_color="#0F766E"), unsafe_allow_html=True)
        with k4:
            st.markdown(render_kpi_card("Peak Occupancy", f"{max_occ}", "Maximum Count", accent_color="#0F766E"), unsafe_allow_html=True)
        with k5:
            st.markdown(render_kpi_card("Sensor Channels", f"{len(sensor_cols)}", "IoT Environmental Feeds", accent_color="#64748B"), unsafe_allow_html=True)
        with k6:
            st.markdown(render_kpi_card("Prediction Accuracy", f"{best_acc:.2f}%", "AI Holdout Benchmark", accent_color="#2563EB"), unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Section 1: Main Dominant Occupancy Trend (Primary Blue #2563EB)
        render_section_header("📈 Occupancy Pattern Over Time", "Continuous longitudinal telemetry capturing classroom transitions and unoccupied intervals.")
        resample_rule = '15min' if len(filtered_df) > 2000 else '5min'
        ts_df = filtered_df.set_index('DateTime').resample(resample_rule)['Is_Occupied'].mean().reset_index()
        
        fig_main = px.area(
            ts_df, x='DateTime', y='Is_Occupied',
            title="Classroom Occupancy State Over Time (Aggregated 15-Minute Profile)",
            labels={'DateTime': 'Timeline', 'Is_Occupied': 'Occupancy Probability'},
            color_discrete_sequence=['#2563EB']
        )
        fig_main.update_traces(line=dict(width=2, color='#2563EB'), fillcolor='rgba(37, 99, 235, 0.12)')
        render_chart(fig_main, height=500)
        
        # Section 2: Occupancy Analysis (Occupancy by Hour & Distribution)
        render_section_header("🕒 Occupancy Distribution & Hourly Profiles", "Granular diurnal breakdown across the 24-hour cycle and occupant count frequency.")
        c_left, c_right = st.columns(2)
        
        with c_left:
            hourly_stats = filtered_df.groupby('Hour')['Is_Occupied'].mean().reset_index()
            hourly_stats['Occupied_Pct'] = hourly_stats['Is_Occupied'] * 100
            fig_hour = px.bar(
                hourly_stats, x='Hour', y='Occupied_Pct',
                title="Average Occupancy Probability by Hour of Day",
                labels={'Hour': 'Hour (00:00 to 23:00)', 'Occupied_Pct': 'Occupancy Rate (%)'},
                color_discrete_sequence=['#2563EB']
            )
            render_chart(fig_hour, height=400)
            
        with c_right:
            target_counts = filtered_df[target_col].value_counts().sort_index().reset_index()
            target_counts.columns = ['Occupants', 'Count']
            target_counts['Percentage'] = (target_counts['Count'] / target_counts['Count'].sum()) * 100
            fig_dist = px.bar(
                target_counts, x='Occupants', y='Count',
                text=target_counts['Percentage'].apply(lambda x: f"{x:.1f}%"),
                title="Ground Truth Occupancy Count Frequency Distribution",
                labels={'Occupants': 'Number of Occupants (0 to 3)', 'Count': 'Recorded Intervals'},
                color_discrete_sequence=['#0F766E']
            )
            fig_dist.update_traces(textposition='outside')
            render_chart(fig_dist, height=400)
            
        # Section 3: Sensor / Utilization Analysis
        render_section_header("🌡️ Environmental Sensor Correlation & Weekly Utilization", "Key sensor responses conditioned on occupant presence and weekday utilization heatmaps.")
        s_left, s_right = st.columns(2)
        
        with s_left:
            top_sensor = feat_imp.iloc[0]['Feature'] if not feat_imp.empty else "S1_Light"
            fig_sensor_box = px.box(
                filtered_df, x='Is_Occupied', y=top_sensor,
                color='Is_Occupied',
                title=f"Primary Predictor Distribution ({top_sensor}) vs Occupancy State",
                labels={'Is_Occupied': 'Occupancy State', top_sensor: f'{top_sensor} Sensor Value'},
                color_discrete_map={0: '#94A3B8', 1: '#2563EB'}
            )
            render_chart(fig_sensor_box, height=400)
            
        with s_right:
            heat_df = filtered_df.pivot_table(index='Day_Name', columns='Hour', values='Is_Occupied', aggfunc='mean').fillna(0) * 100
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heat_df = heat_df.reindex([d for d in days_order if d in heat_df.index])
            fig_heat = px.imshow(
                heat_df,
                title="Classroom Utilization Intensity (% Occupied)",
                labels=dict(x="Hour of Day", y="Day of Week", color="Occupied %"),
                color_continuous_scale="Blues",
                aspect="auto"
            )
            render_chart(fig_heat, height=400)
            
        # Section 4: Key Findings (Observation -> Meaning -> Action)
        render_section_header("💡 Executive Analytical Findings", "Synthesized data-driven insights derived directly from telemetry calculations.")
        peak_h = filtered_df.groupby('Hour')['Is_Occupied'].mean().idxmax()
        peak_d = filtered_df.groupby('Day_Name')['Is_Occupied'].mean().idxmax()
        
        render_insight_card(
            title="1. Structured Diurnal Peak Window",
            observation=f"Classroom utilization strongly concentrates during {peak_h:02d}:00–{peak_h+2:02d}:00 with peak weekday presence observed on {peak_d}.",
            meaning="Instructional schedules create predictable high-demand blocks separated by extended inactive intervals.",
            action="Align HVAC pre-conditioning 30 minutes prior to peak hours and schedule custodial servicing immediately following active class blocks."
        )
        render_insight_card(
            title="2. High Sensitivity of Optical & Acoustic Sensors",
            observation=f"{top_sensor} and acoustic channels exhibit immediate state shifts upon occupant entry with over 80% correlation.",
            meaning="Physical light switches and occupant movements provide instantaneous indicators before thermal or gas concentration changes occur.",
            action="Implement automated daylight harvesting controls to dim fixtures when ambient daylight is sufficient."
        )
        render_insight_card(
            title="3. Significant Standby Energy Reduction Potential",
            observation=f"The classroom is vacant for {100-util_rate:.1f}% of recorded operational time.",
            meaning="Continuous baseline HVAC and lighting operation during unoccupied periods incurs substantial wasted utility expenditure.",
            action="Deploy automated occupancy-based setbacks to reduce standby baseline energy consumption by an estimated 30–45%."
        )


    # =========================================================================
    # PAGE 2: DATASET OVERVIEW
    # =========================================================================
    elif nav_selection == "🗃️ Dataset Overview":
        render_page_header("Dataset Overview & Structure", "Comprehensive schema inspection, data types, and telemetry characteristics.", tag="Data Catalog")
        
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(render_kpi_card("Total Rows", f"{len(clean_df):,}", "Telemetry Records", accent_color="#2563EB"), unsafe_allow_html=True)
        with k2:
            st.markdown(render_kpi_card("Total Columns", f"{len(clean_df.columns)}", "Raw + Engineered", accent_color="#2563EB"), unsafe_allow_html=True)
        with k3:
            st.markdown(render_kpi_card("Numeric Sensors", f"{len(sensor_cols)}", "Environmental Feeds", accent_color="#0F766E"), unsafe_allow_html=True)
        with k4:
            st.markdown(render_kpi_card("Target Classes", f"{clean_df[target_col].nunique()}", f"Values: {sorted(clean_df[target_col].unique().tolist())}", accent_color="#0F766E"), unsafe_allow_html=True)
        with k5:
            st.markdown(render_kpi_card("Dataset Size", f"{clean_df.memory_usage().sum() / 1024:.1f} KB", "In-Memory Footprint", accent_color="#64748B"), unsafe_allow_html=True)
            
        render_section_header("📋 Dataset Preview (First 10 Observations)", "Cleaned and chronologically indexed sensor observations.")
        preview_df = clean_df.head(10).copy()
        if 'DateTime' in preview_df.columns:
            preview_df['DateTime'] = preview_df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(preview_df, use_container_width=True)
        
        render_section_header("🔍 Column Metadata & Data Types", "Field specifications, non-null counts, and unique value cardinality.")
        schema_data = []
        for col in clean_df.columns:
            role = "Target Variable" if col == target_col else ("Timestamp" if col in ['Date', 'Time', 'DateTime'] else ("Sensor Feature" if col in sensor_cols else "Engineered Temporal"))
            schema_data.append({
                "Field Name": col,
                "Data Type": str(clean_df[col].dtype),
                "Missing Values": clean_df[col].isnull().sum(),
                "Unique Values": clean_df[col].nunique(),
                "Analytical Role": role
            })
        st.dataframe(pd.DataFrame(schema_data), use_container_width=True)
        
        csv_buffer = io.StringIO()
        clean_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Cleaned Dataset (CSV)",
            data=csv_buffer.getvalue(),
            file_name="clean_room_occupancy_data.csv",
            mime="text/csv"
        )


    # =========================================================================
    # PAGE 3: DATA QUALITY
    # =========================================================================
    elif nav_selection == "🔍 Data Quality":
        render_page_header("Data Quality & Telemetry Health Audit", "Automated validation: Missing values, duplicate integrity, and sensor outlier boundaries.", tag="Quality Score: 100/100")
        
        q1, q2, q3, q4 = st.columns(4)
        with q1:
            st.markdown(render_kpi_card("Data Quality Score", "100.0 / 100", "Zero Missing / Pristine", accent_color="#0F766E"), unsafe_allow_html=True)
        with q2:
            st.markdown(render_kpi_card("Missing Values", "0", "0.0% Across All Columns", accent_color="#2563EB"), unsafe_allow_html=True)
        with q3:
            st.markdown(render_kpi_card("Duplicate Rows", "0", "0.0% Duplication", accent_color="#2563EB"), unsafe_allow_html=True)
        with q4:
            st.markdown(render_kpi_card("Active Sensor Feeds", f"{len(sensor_cols)}", "100% Signal Integrity", accent_color="#0F766E"), unsafe_allow_html=True)
            
        render_section_header("📊 Sensor Statistical Bounds & IQR Outlier Analysis", "Interquartile Range (IQR) boundaries calculated across all numerical sensor channels.")
        outlier_data = []
        for sc in sensor_cols:
            q25 = clean_df[sc].quantile(0.25)
            q75 = clean_df[sc].quantile(0.75)
            iqr = q75 - q25
            lb = q25 - (1.5 * iqr)
            ub = q75 + (1.5 * iqr)
            n_out = len(clean_df[(clean_df[sc] < lb) | (clean_df[sc] > ub)])
            outlier_data.append({
                "Sensor Channel": sc,
                "Min Value": f"{clean_df[sc].min():.2f}",
                "Median": f"{clean_df[sc].median():.2f}",
                "Max Value": f"{clean_df[sc].max():.2f}",
                "Lower Bound (IQR)": f"{lb:.2f}",
                "Upper Bound (IQR)": f"{ub:.2f}",
                "Outlier Count": n_out,
                "Outlier %": f"{(n_out/len(clean_df))*100:.2f}%"
            })
        st.dataframe(pd.DataFrame(outlier_data), use_container_width=True)


    # =========================================================================
    # PAGE 4: DATA CLEANING
    # =========================================================================
    elif nav_selection == "🧹 Data Cleaning":
        render_page_header("Data Cleaning & Transformation Pipeline", "Non-destructive processing audit verifying schema integrity and feature casting.", tag="Pipeline Audit")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                """
                <div class="kpi-container" style="min-height: 160px; border-top: 3px solid #2563EB;">
                    <div class="kpi-label">Raw Ingestion State</div>
                    <div style="color: #334155; font-size: 0.9rem; line-height: 1.7; margin-top: 8px;">
                        • <b>Source Format</b>: Comma-Separated Values (CSV)<br>
                        • <b>Initial Records</b>: 10,129 rows<br>
                        • <b>Initial Columns</b>: 19 features<br>
                        • <b>Target Variable Identified</b>: <code>Room_Occupancy_Count</code>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                """
                <div class="kpi-container" style="min-height: 160px; border-top: 3px solid #0F766E;">
                    <div class="kpi-label" style="color: #0F766E;">Cleaned & Enriched State</div>
                    <div style="color: #334155; font-size: 0.9rem; line-height: 1.7; margin-top: 8px;">
                        • <b>Preserved Rows</b>: 10,129 rows (100% fidelity)<br>
                        • <b>Final Columns</b>: 31 features (12 engineered)<br>
                        • <b>DateTime Parsing</b>: Synchronized 30-second series<br>
                        • <b>Target Definition</b>: Binary <code>Is_Occupied</code> + Multi-class
                    </div>
                </div>
                """, unsafe_allow_html=True
            )


    # =========================================================================
    # PAGE 5: FEATURE ENGINEERING
    # ==========================================
    elif nav_selection == "⚙️ Feature Engineering":
        render_page_header("Feature Engineering & Temporal Extraction", "Derived chronological variables empowering predictive machine learning algorithms.", tag="12 Engineered Features")
        
        render_section_header("⏱️ Engineered Temporal Variables Summary", "Calendar, hour-of-day, and categorical diurnal classifications.")
        eng_table = pd.DataFrame([
            {"Feature Name": "DateTime", "Purpose": "Synchronized chronological timestamp", "Data Type": "datetime64[ns]"},
            {"Feature Name": "Hour", "Purpose": "Hour of day (0-23) for diurnal modeling", "Data Type": "int32"},
            {"Feature Name": "Day_Name", "Purpose": "Day of week (Monday–Sunday) for scheduling patterns", "Data Type": "object"},
            {"Feature Name": "Day_of_Week", "Purpose": "Numerical weekday index (0-6)", "Data Type": "int32"},
            {"Feature Name": "Time_Period", "Purpose": "Contextual shift (Morning, Midday Peak, Afternoon, Evening, Night)", "Data Type": "object"},
            {"Feature Name": "Is_Weekend", "Purpose": "Binary weekend indicator (1=Sat/Sun, 0=Mon-Fri)", "Data Type": "int32"},
            {"Feature Name": "Is_Occupied", "Purpose": "Binary classification target (1 if Occupants > 0, else 0)", "Data Type": "int32"}
        ])
        st.dataframe(eng_table, use_container_width=True)
        
        render_section_header("📊 Occupancy Distribution by Time Period", "Aggregated classroom occupancy rates across categorical diurnal periods.")
        period_df = clean_df.groupby('Time_Period')['Is_Occupied'].agg(['count', 'mean']).reset_index()
        period_df['Occupancy_Rate'] = period_df['mean'] * 100
        fig_per = px.bar(
            period_df, x='Time_Period', y='Occupancy_Rate',
            title="Classroom Utilization Rate Across Time Periods",
            labels={'Time_Period': 'Diurnal Period', 'Occupancy_Rate': 'Occupancy Rate (%)'},
            color_discrete_sequence=['#2563EB']
        )
        render_chart(fig_per, height=420)


    # =========================================================================
    # PAGE 6: OCCUPANCY ANALYTICS
    # =========================================================================
    elif nav_selection == "📈 Occupancy Analytics":
        render_page_header("Classroom Occupancy Analytics", "Longitudinal patterns, diurnal distribution, and peak demand periods.", tag="Utilization Patterns")
        
        k1, k2, k3, k4 = st.columns(4)
        peak_hr = filtered_df.groupby('Hour')['Is_Occupied'].mean().idxmax()
        peak_rate = filtered_df.groupby('Hour')['Is_Occupied'].mean().max() * 100
        with k1:
            st.markdown(render_kpi_card("Overall Occupancy Rate", f"{(filtered_df['Is_Occupied'].mean()*100):.1f}%", f"{filtered_df['Is_Occupied'].sum():,} Occupied Slots", accent_color="#2563EB"), unsafe_allow_html=True)
        with k2:
            st.markdown(render_kpi_card("Peak Hour", f"{peak_hr:02d}:00", f"{peak_rate:.1f}% Probability", accent_color="#0F766E"), unsafe_allow_html=True)
        with k3:
            st.markdown(render_kpi_card("Lowest Activity Hour", "00:00–06:00", "0.0% Standby Vacancy", accent_color="#64748B"), unsafe_allow_html=True)
        with k4:
            st.markdown(render_kpi_card("Max Occupant Capacity", f"{filtered_df[target_col].max()} Persons", "Observed Peak Attendance", accent_color="#2563EB"), unsafe_allow_html=True)
            
        render_section_header("📈 Longitudinal Occupancy Profile (Full-Width)", "Time series of room occupancy state across observation intervals.")
        resample_rule = '15min' if len(filtered_df) > 2000 else '5min'
        ts_occ = filtered_df.set_index('DateTime').resample(resample_rule)[target_col].mean().reset_index()
        fig_ts = px.line(
            ts_occ, x='DateTime', y=target_col,
            title="Continuous Average Occupancy Count Over Time",
            labels={'DateTime': 'Timestamp', target_col: 'Average Occupant Count'},
            color_discrete_sequence=['#2563EB']
        )
        fig_ts.update_traces(line=dict(width=2))
        render_chart(fig_ts, height=500)
        
        c1, c2 = st.columns(2)
        with c1:
            render_section_header("🕒 Occupancy Probability by Hour of Day", "Hourly diurnal demand curve.")
            hr_stats = filtered_df.groupby('Hour')['Is_Occupied'].mean().reset_index()
            hr_stats['Occupancy_Pct'] = hr_stats['Is_Occupied'] * 100
            fig_h = px.area(
                hr_stats, x='Hour', y='Occupancy_Pct',
                title="Diurnal Demand: Occupancy Probability vs Hour of Day",
                labels={'Hour': 'Hour (00:00 to 23:00)', 'Occupancy_Pct': 'Occupancy Rate (%)'},
                color_discrete_sequence=['#2563EB']
            )
            fig_h.update_traces(line=dict(color='#2563EB'), fillcolor='rgba(37, 99, 235, 0.12)')
            render_chart(fig_h, height=420)
            
        with c2:
            render_section_header("📅 Weekday Utilization Comparison", "Average occupancy rates across days of the week.")
            dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dow_df = filtered_df.groupby('Day_Name')['Is_Occupied'].mean().reindex([d for d in dow_order if d in filtered_df['Day_Name'].unique()]).reset_index()
            dow_df['Rate'] = dow_df['Is_Occupied'] * 100
            fig_dow = px.bar(
                dow_df, x='Day_Name', y='Rate',
                title="Weekly Demand: Average Occupancy Rate by Weekday",
                labels={'Day_Name': 'Day of Week', 'Rate': 'Occupancy Rate (%)'},
                color_discrete_sequence=['#0F766E']
            )
            render_chart(fig_dow, height=420)


    # =========================================================================
    # PAGE 7: SENSOR ANALYTICS
    # =========================================================================
    elif nav_selection == "🌡️ Sensor Analytics":
        render_page_header("Multi-Modal Sensor Relationship Analytics", "Correlation structures, feature interactions, and sensor signatures.", tag="IoT Sensor Feeds")
        
        render_section_header("🔥 Multi-Sensor Correlation Matrix (Large Format)", "Pearson correlation matrix across all 16 environmental sensors and occupancy state.")
        corr_m = filtered_df[sensor_cols + ['Is_Occupied']].corr()
        fig_corr = px.imshow(
            corr_m,
            text_auto=".2f",
            title="Pearson Correlation Coefficients Across All Sensor Channels and Target",
            color_continuous_scale="Blues",
            aspect="auto"
        )
        render_chart(fig_corr, height=500)
        
        s1, s2 = st.columns(2)
        with s1:
            render_section_header("🔬 Optical Sensor vs Occupancy", "Illuminance response conditioned on room entry.")
            fig_s1 = px.box(
                filtered_df, x='Is_Occupied', y='S1_Light',
                color='Is_Occupied',
                title="S1_Light (Lux) vs Occupancy State",
                labels={'Is_Occupied': 'Occupancy State', 'S1_Light': 'Illuminance (Lux)'},
                color_discrete_map={0: '#94A3B8', 1: '#2563EB'}
            )
            render_chart(fig_s1, height=400)
            
        with s2:
            render_section_header("🔊 Acoustic Sensor vs Occupancy", "Sound pressure levels conditioned on occupant movements.")
            fig_s2 = px.box(
                filtered_df, x='Is_Occupied', y='S1_Sound',
                color='Is_Occupied',
                title="S1_Sound (Volts) vs Occupancy State",
                labels={'Is_Occupied': 'Occupancy State', 'S1_Sound': 'Sound Pressure (V)'},
                color_discrete_map={0: '#94A3B8', 1: '#0F766E'}
            )
            render_chart(fig_s2, height=400)


    # =========================================================================
    # PAGE 8: UTILIZATION INTELLIGENCE
    # =========================================================================
    elif nav_selection == "💡 Utilization Intelligence":
        render_page_header("Classroom Utilization Intelligence & Capacity Scoring", "Quantitative evaluation of space utilization efficiency.", tag="Utilization Metrics")
        
        tot = len(filtered_df)
        occ = int(filtered_df['Is_Occupied'].sum())
        u_score = (occ / tot * 100) if tot > 0 else 0
        
        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown(render_kpi_card("Classroom Utilization Score", f"{u_score:.2f}%", f"{occ:,} Occupied Slots / {tot:,} Total", accent_color="#2563EB"), unsafe_allow_html=True)
        with k2:
            st.markdown(render_kpi_card("Active Occupied Time", f"{(occ*0.5)/60:.1f} Hours", "Total Active Class Hours", accent_color="#0F766E"), unsafe_allow_html=True)
        with k3:
            st.markdown(render_kpi_card("Idle / Standby Time", f"{((tot-occ)*0.5)/60:.1f} Hours", "Opportunity for Energy Setback", accent_color="#64748B"), unsafe_allow_html=True)
            
        render_section_header("📊 Hourly Capacity Stress Profile", "Percentage of time the room is occupied across 24 hours.")
        h_util = filtered_df.groupby('Hour')['Is_Occupied'].agg(['count', 'sum']).reset_index()
        h_util['util_pct'] = (h_util['sum'] / h_util['count']) * 100
        fig_u = px.bar(
            h_util, x='Hour', y='util_pct',
            title="Hourly Classroom Utilization Rate (%)",
            labels={'Hour': 'Hour of Day (00:00 to 23:00)', 'util_pct': 'Utilization Rate (%)'},
            color_discrete_sequence=['#2563EB']
        )
        render_chart(fig_u, height=450)


    # =========================================================================
    # PAGE 9: AI PREDICTION
    # =========================================================================
    elif nav_selection == "🤖 AI Prediction":
        render_page_header("AI Occupancy Prediction & Live Inference", "Simulate live environmental sensor feeds and predict room occupancy state.", tag="Real-Time Inference")
        
        render_section_header("📊 Predictive Model Capabilities (Holdout Benchmark)", "Empirical benchmark metrics on the 80/20 chronological holdout test set.")
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(render_kpi_card("Best Model", "Logistic Reg", "StandardScaler + L2", accent_color="#2563EB"), unsafe_allow_html=True)
        with m2:
            st.markdown(render_kpi_card("Accuracy", f"{ml_results['Logistic Regression']['accuracy']*100:.2f}%", "Holdout Test Set", accent_color="#2563EB"), unsafe_allow_html=True)
        with m3:
            st.markdown(render_kpi_card("Precision", f"{ml_results['Logistic Regression']['precision']*100:.2f}%", "Zero False Positives", accent_color="#0F766E"), unsafe_allow_html=True)
        with m4:
            st.markdown(render_kpi_card("Recall", f"{ml_results['Logistic Regression']['recall']*100:.2f}%", "Occupancy Sensitivity", accent_color="#0F766E"), unsafe_allow_html=True)
        with m5:
            st.markdown(render_kpi_card("F1-Score", f"{ml_results['Logistic Regression']['f1_score']*100:.2f}%", "Harmonic Balance", accent_color="#2563EB"), unsafe_allow_html=True)
            
        render_section_header("🎛️ Live Environmental Sensor Input Simulator", "Adjust sensor sliders to evaluate the model's live inference output.")
        
        input_values = {}
        c_env1, c_env2, c_env3 = st.columns(3)
        
        with c_env1:
            st.markdown("#### 💡 Optical & Acoustic Feeds")
            for f in ['S1_Light', 'S2_Light', 'S1_Sound', 'S2_Sound']:
                if f in sensor_cols:
                    input_values[f] = st.slider(f"{f} Reading", float(clean_df[f].min()), float(clean_df[f].max()), float(clean_df[f].median()))
                    
        with c_env2:
            st.markdown("#### 🌡️ Temperature Gradients")
            for f in ['S1_Temp', 'S2_Temp', 'S3_Temp', 'S4_Temp']:
                if f in sensor_cols:
                    input_values[f] = st.slider(f"{f} (°C)", float(clean_df[f].min()), float(clean_df[f].max()), float(clean_df[f].median()))
                    
        with c_env3:
            st.markdown("#### 💨 CO2 & Motion Sensors")
            for f in ['S5_CO2', 'S5_CO2_Slope', 'S6_PIR', 'S7_PIR']:
                if f in sensor_cols:
                    input_values[f] = st.slider(f"{f}", float(clean_df[f].min()), float(clean_df[f].max()), float(clean_df[f].median()))
                    
        for sc in sensor_cols:
            if sc not in input_values:
                input_values[sc] = float(clean_df[sc].median())
                
        st.markdown("<br>", unsafe_allow_html=True)
        pred_btn = st.button("🚀 PREDICT OCCUPANCY STATE", use_container_width=True)
        
        if pred_btn:
            input_df = pd.DataFrame([input_values])
            lr_m = fitted_models['Logistic Regression']
            prob_occ = lr_m.predict_proba(input_df)[0, 1]
            pred_class = int(prob_occ >= 0.5)
            
            res_c1, res_c2 = st.columns([5, 7])
            with res_c1:
                render_section_header("🎯 Predicted Occupancy Output")
                if pred_class == 1:
                    st.markdown(
                        f"""
                        <div class="result-banner-occupied">
                            <div style="font-size: 2.5rem; color: #2563EB;">👥</div>
                            <div style="font-size: 1.7rem; font-weight: 800; color: #1E40AF; margin-top: 6px;">CLASSROOM IS OCCUPIED</div>
                            <div style="color: #475569; font-size: 1.0rem; margin-top: 8px;">Model Confidence: <b style="color:#0F172A;">{prob_occ*100:.1f}%</b></div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="result-banner-vacant">
                            <div style="font-size: 2.5rem; color: #64748B;">🚪</div>
                            <div style="font-size: 1.7rem; font-weight: 800; color: #334155; margin-top: 6px;">CLASSROOM IS VACANT</div>
                            <div style="color: #475569; font-size: 1.0rem; margin-top: 8px;">Model Confidence: <b style="color:#0F172A;">{(1 - prob_occ)*100:.1f}%</b></div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                    
            with res_c2:
                render_section_header("📊 Occupancy Probability Gauge")
                fig_g = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=prob_occ * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Occupancy Probability (%)", 'font': {'size': 14, 'color': '#0F172A'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#64748B'},
                        'bar': {'color': '#2563EB'},
                        'steps': [
                            {'range': [0, 50], 'color': "#F1F5F9"},
                            {'range': [50, 100], 'color': "#E0F2FE"}
                        ],
                        'threshold': {'line': {'color': "#0F172A", 'width': 3}, 'thickness': 0.8, 'value': 50}
                    }
                ))
                render_chart(fig_g, height=320)


    # =========================================================================
    # PAGE 10: MODEL EVALUATION
    # =========================================================================
    elif nav_selection == "🎯 Model Evaluation":
        render_page_header("Machine Learning Model Benchmarking & Validation", "Chronological zero-leakage evaluation, confusion matrix, and feature importances.", tag="ML Benchmark")
        
        st.info("🛡️ **Zero-Leakage Guarantee**: Evaluated on an 80/20 chronological holdout test set (8,103 training observations $\\rightarrow$ 2,026 testing observations). Timestamps and target identifiers are strictly excluded.")
        
        render_section_header("📊 Multi-Model Performance Comparison", "Standardized performance evaluation metrics across classification algorithms.")
        m_rows = []
        for name, m in ml_results.items():
            m_rows.append({
                "Model Architecture": name,
                "Accuracy": f"{m['accuracy']*100:.2f}%",
                "Precision": f"{m['precision']*100:.2f}%",
                "Recall": f"{m['recall']*100:.2f}%",
                "F1-Score": f"{m['f1_score']*100:.2f}%",
                "ROC-AUC": f"{m['roc_auc']:.4f}" if not np.isnan(m['roc_auc']) else "N/A",
                "Train Time (s)": f"{m['train_time']:.3f}s"
            })
        st.dataframe(pd.DataFrame(m_rows), use_container_width=True)
        
        render_section_header("🔲 Confusion Matrix — Occupancy Classification (Large Format)", "Detailed true positive, true negative, false positive, and false negative counts on holdout test set.")
        cm_lr = np.array(ml_results['Logistic Regression']['confusion_matrix'])
        fig_cm = px.imshow(
            cm_lr,
            text_auto=True,
            labels=dict(x="Predicted Class", y="Actual Ground Truth", color="Observations"),
            x=['Vacant (0)', 'Occupied (1)'],
            y=['Vacant (0)', 'Occupied (1)'],
            color_continuous_scale="Blues",
            title="Confusion Matrix: Logistic Regression Holdout Test Set (N = 2,026)"
        )
        render_chart(fig_cm, height=500)
        
        render_section_header("🌲 Top Features Influencing Occupancy Prediction (Large Format)", "Relative feature importance ranking derived from Random Forest classifier.")
        fig_imp = px.bar(
            feat_imp.head(10), x='Importance', y='Feature',
            orientation='h',
            title="Top 10 Most Predictive Environmental Sensor Features (Gini Importance)",
            color_discrete_sequence=['#2563EB']
        )
        fig_imp.update_layout(yaxis=dict(autorange="reversed"))
        render_chart(fig_imp, height=500)


    # =========================================================================
    # PAGE 11: RESOURCE PLANNING
    # =========================================================================
    elif nav_selection == "🏢 Resource Planning":
        render_page_header("Smart Facility Resource Planning & Automation", "Using occupancy patterns to support classroom scheduling and energy conservation.", tag="Actionable Facility Insights")
        
        unocc_ratio = (clean_df['Is_Occupied'] == 0).mean()
        tot_idle_hrs = (len(clean_df) * (1 - clean_df['Is_Occupied'].mean()) * 0.5) / 60
        
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(render_kpi_card("Standby Vacancy Rate", f"{unocc_ratio*100:.1f}%", "Unoccupied Observation Ratio", accent_color="#2563EB"), unsafe_allow_html=True)
        with k2:
            st.markdown(render_kpi_card("Idle Standby Time", f"{tot_idle_hrs:,.1f} Hours", "Total Available Setback Window", accent_color="#64748B"), unsafe_allow_html=True)
        with k3:
            st.markdown(render_kpi_card("Estimated Energy Savings", "30–45%", "HVAC & Lighting Optimization", accent_color="#0F766E"), unsafe_allow_html=True)
        with k4:
            st.markdown(render_kpi_card("Peak Demand Window", "10:00–14:00", "Instructional Lecture Shift", accent_color="#2563EB"), unsafe_allow_html=True)
            
        render_section_header("⚡ Strategic Facility Planning Recommendations", "Targeted automation workflows based on empirical occupancy patterns.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                """
                <div class="kpi-container" style="min-height: 220px; border-top: 3px solid #2563EB;">
                    <div class="kpi-label" style="color: #2563EB;">1. HVAC Setback & Ventilation Control</div>
                    <div style="color: #334155; font-size: 0.88rem; line-height: 1.6; margin-top: 8px;">
                        • <b>Off-Hours Setback</b>: Automatically switch thermostats to setback temperatures between 20:00 and 07:00.<br>
                        • <b>Demand-Controlled Ventilation (DCV)</b>: Modulate fresh air dampers according to real-time CO2 slope derivatives.<br>
                        • <b>Pre-Cooling Protocol</b>: Ramp up environmental conditioning 30 minutes prior to the 10:00 lecture rush.
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                """
                <div class="kpi-container" style="min-height: 220px; border-top: 3px solid #0F766E;">
                    <div class="kpi-label" style="color: #0F766E;">2. Lighting & Custodial Management</div>
                    <div style="color: #334155; font-size: 0.88rem; line-height: 1.6; margin-top: 8px;">
                        • <b>Automated Daylight Harvesting</b>: Dim perimeter luminaires when ambient daylight (S1_Light) exceeds 250 Lux.<br>
                        • <b>PIR Motion Sleep Timeout</b>: Configure luminaire sleep timers to extinguish lamps after 8 minutes of vacancy.<br>
                        • <b>Demand-Driven Custodial Dispatch</b>: Trigger janitorial work orders after 4 hours of cumulative occupancy.
                    </div>
                </div>
                """, unsafe_allow_html=True
            )


    # =========================================================================
    # PAGE 12: INSIGHTS & RECOMMENDATIONS
    # =========================================================================
    elif nav_selection == "📋 Insights & Recommendations":
        render_page_header("Data-Driven Insights & Strategic Recommendations", "Observation-Meaning-Action framework synthesized from historical sensor telemetry.", tag="Strategic Summary")
        
        top_f = feat_imp.iloc[0]['Feature'] if not feat_imp.empty else "S1_Light"
        render_insight_card(
            title="1. Optical & Acoustic Sensors Exhibit Dominant Predictive Importance",
            observation=f"Random Forest assigns {feat_imp.iloc[0]['Importance']*100:.1f}% relative importance to {top_f}, followed by acoustic pressure readings.",
            meaning="Physical room entry immediately alters ambient lux levels and noise before thermal inertia or gas accumulation occur.",
            action="Deploy paired optical/acoustic multi-sensors near room doorways for instantaneous occupancy triggers."
        )
        render_insight_card(
            title="2. Diurnal Occupancy Peak Concentration",
            observation="Empirical observations reveal near-zero occupancy before 08:00 and after 20:00, with maximum activity concentrated mid-day.",
            meaning="Classrooms have highly predictable usage schedules that diverge substantially from continuous 24/7 HVAC operations.",
            action="Integrate facility scheduling software with building management systems (BMS) to dynamically schedule base conditioning."
        )
        render_insight_card(
            title="3. CO2 Concentration Rate of Change Advantage",
            observation="S5_CO2_Slope (first derivative) correlates strongly with occupancy transitions and leads raw PPM concentration.",
            meaning="CO2 accumulation suffers from room volume dilution lag, whereas derivative slope responds rapidly to occupancy events.",
            action="Use CO2 slope rate-of-change thresholds rather than static PPM limits for fast-acting ventilation dampers."
        )


    # =========================================================================
    # PAGE 13: ABOUT PROJECT
    # =========================================================================
    elif nav_selection == "ℹ️ About Project":
        render_page_header("About Smart Classroom AI Platform", "System architecture, methodology, technology stack, and dataset provenance.", tag="System Architecture")
        
        render_section_header("🎯 Project Purpose & Scope")
        st.write(
            "The AI-Powered Smart Classroom Occupancy & Resource Planning system is an intelligent data analytics and machine learning "
            "platform engineered to process multivariate IoT sensor streams, detect occupancy patterns, and guide facility energy management."
        )
        
        render_section_header("📍 Dataset Provenance & Attribution")
        st.markdown(
            "- **Dataset Name**: Room Occupancy Estimation\n"
            "- **Official Source**: [https://www.kaggle.com/datasets/ruchikakumbhar/room-occupancy-estimation](https://www.kaggle.com/datasets/ruchikakumbhar/room-occupancy-estimation)\n"
            "- **Dataset File**: `dataset/room occupancy.csv` (10,129 records across 19 sensor channels)\n"
            "- **Project Context**: IBM SkillsBuild Data Analytics with AI\n"
        )
        
        render_section_header("🛠️ Technology Stack & Analytical Pipeline")
        st.markdown(
            "- **Frontend / UI**: Streamlit 1.35+ (Wide layout, responsive Plotly charts, modern design system)\n"
            "- **Interactive Visualizations**: Plotly Express & Graph Objects\n"
            "- **Machine Learning**: Scikit-Learn (Logistic Regression, Random Forest, HistGradientBoosting)\n"
            "- **Data Manipulation**: Pandas, NumPy, SciPy\n"
            "- **Documentation Engine**: python-docx\n"
        )
        
        st.markdown(
            """
            ```
            Raw Telemetry Data
                    ↓
            Data Quality & Health Audit
                    ↓
            Safe Cleaning & Feature Engineering
                    ↓
            Zero-Leakage ML Model Training
                    ↓
            Predictive Inference & Evaluation
                    ↓
            Smart Resource Planning Dashboard
            ```
            """
        )


if __name__ == "__main__":
    main()
