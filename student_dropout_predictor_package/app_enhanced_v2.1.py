import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import shap
import pickle
import io
from openai import OpenAI
import os
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Student Dropout Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PROFESSIONAL UI/UX STYLING
# ============================================================================
st.markdown("""
<style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e293b;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    /* Cards and Containers */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s, box-shadow 0.2s;
        margin: 0.5rem 0;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .prediction-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border: 2px solid #e2e8f0;
        margin: 1.5rem 0;
    }
    
    /* Risk Status Cards */
    .risk-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 20px 25px -5px rgba(255, 107, 107, 0.3);
        border: 3px solid rgba(255, 255, 255, 0.3);
    }
    
    .risk-low {
        background: linear-gradient(135deg, #51cf66 0%, #37b24d 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 20px 25px -5px rgba(81, 207, 102, 0.3);
        border: 3px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 5px solid #2196f3;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #0d47a1;
        font-size: 0.95rem;
        line-height: 1.6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left: 5px solid #ff9800;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #e65100;
        font-size: 0.95rem;
        line-height: 1.6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .success-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 5px solid #4caf50;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #1b5e20;
        font-size: 0.95rem;
        line-height: 1.6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Input Fields Enhancement */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stSlider > div > div > div,
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.2s !important;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(102, 126, 234, 0.3);
        transition: all 0.3s;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.4);
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #64748b;
        transition: all 0.2s;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Radio Buttons */
    .stRadio > div {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        border: 2px dashed #cbd5e1;
        transition: all 0.2s;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: #f8f9ff;
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 0.95rem;
        font-weight: 600;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(72, 187, 120, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 10px -2px rgba(72, 187, 120, 0.4);
    }
    
    /* Sidebar Enhancements */
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    /* Status Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 10px;
        padding: 1rem;
        font-weight: 500;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    }
    
    /* Caption Text */
    .stCaption {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Slider Enhancement */
    .stSlider {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD MODEL AND RESOURCES
# ============================================================================
@st.cache_resource
def load_resources():
    """Load model, scaler, feature names, and initialize SHAP explainer"""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        with open(os.path.join(base_path, 'random_forest_dropout_model.pkl'), 'rb') as f:
            model = pickle.load(f)
        with open(os.path.join(base_path, 'scaler.pkl'), 'rb') as f:
            scaler = pickle.load(f)
        with open(os.path.join(base_path, 'feature_names.pkl'), 'rb') as f:
            feature_names = pickle.load(f)
        
        explainer = shap.TreeExplainer(model)
        
        try:
            api_key = os.getenv("NVIDIA_API_KEY", "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")
            client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)
        except:
            client = None
        
        return model, scaler, feature_names, explainer, client
    except Exception as e:
        st.error(f"Error loading resources: {str(e)}")
        st.stop()

model, scaler, feature_names, explainer, nim_client = load_resources()


# ============================================================================
# PHASE 1 UX ENHANCEMENTS - Helper Functions
# ============================================================================

def validate_input_field(value, min_val, max_val, field_name):
    """Validate numeric input and return status with message"""
    if value < min_val or value > max_val:
        return False, f"⚠️ {field_name} must be between {min_val} and {max_val}"
    return True, f"✓ Valid"

def show_help_tooltip(text, example=""):
    """Display contextual help tooltip"""
    with st.expander("ℹ️ Help"):
        st.info(text)
        if example:
            st.caption(f"**Example:** {example}")

def show_empty_state(icon, title, description, action_text="", action_link=""):
    """Display friendly empty state"""
    st.markdown(f"""
    <div style='text-align: center; padding: 4rem 2rem; color: #94a3b8;'>
        <div style='font-size: 5rem; margin-bottom: 1.5rem; opacity: 0.6;'>{icon}</div>
        <h3 style='color: #64748b; margin-bottom: 1rem;'>{title}</h3>
        <p style='font-size: 1.1rem; line-height: 1.8; max-width: 500px; margin: 0 auto;'>
            {description}
        </p>
    </div>
    """, unsafe_allow_html=True)
    if action_text:
        st.info(f"👉 **Next Step:** {action_text}")

def enhanced_number_input_with_validation(label, min_value, max_value, default, step, key, help_text, example=""):
    """Enhanced number input with inline validation"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        value = st.number_input(label, min_value, max_value, default, step, key=key, help=help_text)
    
    with col2:
        is_valid, msg = validate_input_field(value, min_value, max_value, label)
        if is_valid:
            st.success("✓")
        else:
            st.error("✗")
    
    if not is_valid:
        st.caption(f"⚠️ {msg}")
    
    if example and is_valid:
        st.caption(f"💡 {example}")
    
    return value

def show_welcome_tutorial():
    """Display welcome tutorial modal for first-time users"""
    if st.session_state.show_tutorial:
        st.markdown("""
        <div style='background: white; padding: 2.5rem; border-radius: 20px; box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15); margin: 2rem 0;'>
            <h2 style='color: #667eea; margin-bottom: 1rem;'>🎓 Welcome to Student Dropout Predictor!</h2>
            
            <p style='font-size: 1.1rem; line-height: 1.8; color: #475569; margin-bottom: 1.5rem;'>
                This AI-powered system helps identify students at risk of dropping out with <strong>88.43% accuracy</strong>.
            </p>
            
            <div style='background: #f8f9ff; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0;'>
                <h4 style='color: #667eea; margin-bottom: 1rem;'>✨ Quick Start Guide:</h4>
                <ul style='line-height: 2; color: #475569;'>
                    <li><strong>Individual Assessment:</strong> Predict risk for a single student with AI explanations</li>
                    <li><strong>Batch Processing:</strong> Analyze entire cohorts at once via CSV upload</li>
                    <li><strong>Analytics Dashboard:</strong> Explore model performance and feature importance</li>
                </ul>
            </div>
            
            <div style='background: #fff3e0; padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
                <p style='margin: 0; color: #e65100;'>
                    <strong>💡 Tip:</strong> Hover over any field label for helpful explanations and examples!
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🚀 Get Started", use_container_width=True):
                st.session_state.show_tutorial = False
                st.rerun()
        with col2:
            if st.button("Don't show again", use_container_width=True):
                st.session_state.show_tutorial = False
                st.rerun()

def enhanced_loading_state(message="Processing...", progress=None):
    """Enhanced loading indicator with progress"""
    with st.spinner(f"⚙️ {message}"):
        if progress is not None:
            progress_bar = st.progress(progress)
            return progress_bar
        return None

def export_chart_button(fig, filename_prefix):
    """Add export functionality to charts"""
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button(f"📥 Export", key=f"export_{filename_prefix}", help="Download this chart as PNG"):
            # Note: This requires plotly.io which needs kaleido package
            try:
                import plotly.io as pio
                img_bytes = pio.to_image(fig, format="png", width=1200, height=800)
                st.download_button(
                    "Download PNG",
                    img_bytes,
                    file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    key=f"dl_{filename_prefix}"
                )
            except:
                st.warning("📦 Install kaleido package to enable chart export: `pip install kaleido`")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def age_to_group(age):
    """Convert age to age group bucket: 0=17-20, 1=21-25, 2=26+"""
    if age <= 20:
        return 0
    elif age <= 25:
        return 1
    else:
        return 2

def calculate_financial_stress(is_debtor, tuition_up_to_date, has_scholarship):
    """Formula: (Debtor * 0.4) + ((1 - Tuition up to date) * 0.4) + ((1 - Scholarship) * 0.2)"""
    return (is_debtor * 0.4) + ((1 - tuition_up_to_date) * 0.4) + ((1 - has_scholarship) * 0.2)

def calculate_deltas(sem1_grade, sem1_approved, sem1_enrolled, sem2_grade, sem2_approved, sem2_enrolled):
    """Calculate delta features"""
    grade_delta = sem2_grade - sem1_grade
    approved_delta = sem2_approved - sem1_approved
    
    if sem1_enrolled > 0 and sem2_enrolled > 0:
        efficiency_1st = sem1_approved / sem1_enrolled
        efficiency_2nd = sem2_approved / sem2_enrolled
        efficiency_change = efficiency_2nd - efficiency_1st
    else:
        efficiency_change = 0.0
    
    return grade_delta, approved_delta, efficiency_change

def get_prediction(input_values):
    input_df = pd.DataFrame([input_values], columns=feature_names)
    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)[0]
    probabilities = model.predict_proba(input_scaled)[0]
    return prediction, probabilities

def get_shap_values(input_values):
    input_df = pd.DataFrame([input_values], columns=feature_names)
    shap_values = explainer.shap_values(input_df)
    if len(shap_values.shape) == 3:
        return np.array(shap_values[0, :, 1]).flatten()
    return np.array(shap_values[0, :]).flatten()

def get_ai_explanation(input_values, prediction, probabilities, top_factors):
    if nim_client is None:
        return "NVIDIA NIM API not configured. Set NVIDIA_API_KEY environment variable to enable AI explanations."
    
    dropout_prob = probabilities[1] * 100
    prompt = f"""Explain this dropout prediction in 4-6 sentences.
Outcome: {'Dropout' if prediction == 1 else 'Graduate'} ({dropout_prob:.1f}%)
Top factors: {', '.join([f"{r['feature']}={r['value']:.2f}" for _, r in top_factors.iterrows()])}
Provide actionable insights."""
    
    try:
        completion = nim_client.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Could not generate AI explanation: {str(e)}"

# ============================================================================
# ENHANCED VISUALIZATIONS
# ============================================================================

def plot_probability_gauge(probabilities):
    dropout_prob = probabilities[1] * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dropout_prob,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Dropout Probability", 'font': {'size': 26, 'color': '#1e293b', 'family': 'Arial'}},
        number={'font': {'size': 50, 'color': '#1e293b', 'family': 'Arial Bold'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#cbd5e1"},
            'bar': {'color': "#667eea", 'thickness': 0.8},
            'bgcolor': "white",
            'borderwidth': 3,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, 30], 'color': '#d1fae5'},
                {'range': [30, 70], 'color': '#fef3c7'},
                {'range': [70, 100], 'color': '#fecaca'}
            ],
            'threshold': {
                'line': {'color': "#dc2626", 'width': 6},
                'thickness': 0.85,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Arial, sans-serif'}
    )
    return fig

def plot_shap_waterfall(shap_values, input_values):
    df = pd.DataFrame({
        'feature': feature_names,
        'shap': shap_values
    }).sort_values('shap', key=abs, ascending=False).head(10)
    
    colors = ['#ef4444' if x > 0 else '#10b981' for x in df['shap']]
    
    fig = go.Figure(go.Bar(
        y=df['feature'],
        x=df['shap'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.1)', width=1)
        ),
        text=[f"{x:+.4f}" for x in df['shap']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>SHAP: %{x:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "Top 10 Feature Impacts on Prediction",
            'font': {'size': 20, 'color': '#1e293b', 'family': 'Arial Bold'}
        },
        xaxis_title="SHAP Value (Impact)",
        yaxis_title="",
        height=550,
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Arial, sans-serif', 'size': 12},
        margin=dict(l=20, r=20, t=60, b=40),
        xaxis={'gridcolor': '#f1f5f9', 'zerolinecolor': '#cbd5e1', 'zerolinewidth': 2}
    )
    
    return fig

def plot_risk_distribution(results_df):
    risk_cat = pd.cut(results_df['dropout_prob'], bins=[0,30,70,100], 
                      labels=['Low Risk (<30%)', 'Medium Risk (30-70%)', 'High Risk (>70%)'])
    counts = risk_cat.value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.4,
        marker=dict(colors=['#10b981', '#fbbf24', '#ef4444'], line=dict(color='white', width=3)),
        textfont=dict(size=14, family='Arial Bold', color='white'),
        hovertemplate='<b>%{label}</b><br>%{value} students (%{percent})<extra></extra>'
    )])
    
    fig.update_layout(
        title={'text': "Risk Level Distribution", 'font': {'size': 20, 'color': '#1e293b', 'family': 'Arial Bold'}},
        height=450,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=12)),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Arial, sans-serif'}
    )
    
    return fig

def plot_probability_histogram(results_df):
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=results_df['dropout_prob'],
        nbinsx=20,
        marker=dict(color='#667eea', line=dict(color='white', width=1)),
        hovertemplate='Probability: %{x:.1f}%<br>Count: %{y}<extra></extra>'
    ))
    
    fig.add_vline(x=30, line_dash="dash", line_color="#10b981", line_width=3, 
                  annotation_text="Low Risk", annotation_position="top left")
    fig.add_vline(x=70, line_dash="dash", line_color="#ef4444", line_width=3,
                  annotation_text="High Risk", annotation_position="top right")
    
    fig.update_layout(
        title={'text': "Distribution of Dropout Probabilities", 'font': {'size': 20, 'color': '#1e293b', 'family': 'Arial Bold'}},
        xaxis_title="Dropout Probability (%)",
        yaxis_title="Number of Students",
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Arial, sans-serif'},
        xaxis={'gridcolor': '#f1f5f9'},
        yaxis={'gridcolor': '#f1f5f9'}
    )
    
    return fig

# ============================================================================
# PAGE: SINGLE PREDICTION
# ============================================================================

def page_single_prediction():
    st.markdown("<h1 class='main-header'>Individual Student Risk Assessment</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Predict dropout risk with AI-powered insights and explainable features</p>", unsafe_allow_html=True)
    
    # Input mode selection in a card
    st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
    input_mode = st.radio(
        "Select Input Method",
        ["📊 Smart Input - Auto-calculate performance metrics", "✏️ Manual Input - Enter all features directly"],
        help="Smart input calculates deltas automatically from semester data"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    if "Smart" in input_mode:
        # Semester Performance Section
        st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>📚 Academic Performance</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("#### 🔵 First Semester")
            sem1_grade = st.number_input("Grade (0-20 scale)", 0.0, 20.0, 12.5, 0.1, key="s1g",
                                        help="Average grade in first semester")
            sem1_approved = st.number_input("Courses Approved", 0, 30, 5, key="s1a",
                                           help="Number of courses successfully completed")
            sem1_enrolled = st.number_input("Courses Enrolled", 0, 30, 6, key="s1e",
                                           help="Total courses enrolled in")
        
        with col2:
            st.markdown("#### 🟢 Second Semester")
            sem2_grade = st.number_input("Grade (0-20 scale)", 0.0, 20.0, 11.8, 0.1, key="s2g",
                                        help="Average grade in second semester")
            sem2_approved = st.number_input("Courses Approved", 0, 30, 4, key="s2a",
                                           help="Number of courses successfully completed")
            sem2_enrolled = st.number_input("Courses Enrolled", 0, 30, 6, key="s2e",
                                           help="Total courses enrolled in")
        
        grade_delta, approved_delta, efficiency_change = calculate_deltas(
            sem1_grade, sem1_approved, sem1_enrolled, sem2_grade, sem2_approved, sem2_enrolled)
        
        st.markdown("#### 📊 Calculated Performance Trends")
        col_d1, col_d2, col_d3 = st.columns(3)
        
        delta_color = "normal" if grade_delta >= 0 else "inverse"
        col_d1.metric("Grade Change", f"{grade_delta:+.2f}", 
                     delta=f"{abs(grade_delta):.2f} {'improvement' if grade_delta >= 0 else 'decline'}",
                     delta_color=delta_color)
        col_d2.metric("Approved Courses Change", f"{approved_delta:+d}",
                     delta=f"{abs(approved_delta)} {'more' if approved_delta >= 0 else 'fewer'}")
        col_d3.metric("Efficiency Change", f"{efficiency_change:+.3f}",
                     delta=f"{abs(efficiency_change):.3f} {'better' if efficiency_change >= 0 else 'worse'}",
                     delta_color="normal" if efficiency_change >= 0 else "inverse")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Student Profile Section
        st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>👤 Student Demographics & Background</p>", unsafe_allow_html=True)
        
        col3, col4 = st.columns(2, gap="large")
        
        with col3:
            age = enhanced_number_input_with_validation(
                "Age", 17, 70, 20, 1, "age_input",
                "Student age in years",
                "Typical range: 18-25 for traditional students, 26+ for mature students"
            )
            age_group = age_to_group(age)
            st.caption(f"🔹 Age Category: **{['17-20 years', '21-25 years', '26+ years'][age_group]}**")
            
            admission_grade = st.number_input("Admission Grade (0-200)", 0.0, 200.0, 125.0, 1.0,
                                             help="Grade at university admission")
            unemployment = st.number_input("Regional Unemployment Rate (%)", 0.0, 30.0, 10.5, 0.5,
                                          help="Unemployment rate in student's region")
        
        with col4:
            prev_qual = st.number_input("Previous Qualification Code", 0, 20, 1,
                                       help="Type of secondary education completed")
            course = st.number_input("Course Code", 0, 10000, 9238,
                                    help="Enrolled program identifier")
            attendance = st.selectbox("Attendance Schedule", [1, 0], 
                                     format_func=lambda x: "☀️ Daytime Classes" if x==1 else "🌙 Evening Classes",
                                     help="Class timing preference")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Financial Information Section
        st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>💰 Financial Information</p>", unsafe_allow_html=True)
        
        col5, col6, col7 = st.columns(3)
        
        with col5:
            is_debtor = st.selectbox("Outstanding Debt", [0, 1], 
                                    format_func=lambda x: "❌ No" if x==0 else "⚠️ Yes",
                                    help="Has outstanding financial debt")
        with col6:
            tuition_up_to_date = st.selectbox("Tuition Payment Status", [1, 0], 
                                             format_func=lambda x: "✅ Current" if x==1 else "⚠️ Overdue",
                                             help="Whether tuition fees are paid")
        with col7:
            has_scholarship = st.selectbox("Scholarship Status", [0, 1], 
                                          format_func=lambda x: "❌ None" if x==0 else "✅ Active",
                                          help="Has active scholarship")
        
        financial_stress = calculate_financial_stress(is_debtor, tuition_up_to_date, has_scholarship)
        
        # Financial stress indicator with color coding
        stress_color = "#ef4444" if financial_stress > 0.6 else ("#fbbf24" if financial_stress > 0.3 else "#10b981")
        st.markdown(f"""
        <div style='background: white; padding: 1rem; border-radius: 10px; border-left: 5px solid {stress_color}; margin-top: 1rem;'>
            <strong>Calculated Financial Stress Index:</strong> 
            <span style='font-size: 1.3rem; color: {stress_color}; font-weight: 700;'>{financial_stress:.3f}</span>
            <br><small style='color: #64748b;'>Formula: (Debt * 0.4) + (Overdue Tuition * 0.4) + (No Scholarship * 0.2)</small>
        </div>        
        # Show help for financial stress calculation
        with st.expander("ℹ️ How is Financial Stress Index calculated?"):
            st.markdown("""
            **Formula:** `(Debt * 0.4) + (Overdue Tuition * 0.4) + (No Scholarship * 0.2)`
            
            **Interpretation:**
            * **< 0.3** (Green): Low financial stress
            * **0.3 - 0.6** (Yellow): Moderate financial stress  
            * **> 0.6** (Red): High financial stress
            
            This composite score weighs debt and tuition payment status more heavily than scholarship status.
            """)
        

        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Additional Factors Section
        st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>📈 Additional Risk Factors</p>", unsafe_allow_html=True)
        
        absenteeism_trend = st.slider(
            "Absenteeism Trend (0 = Excellent Attendance, 1 = Frequently Absent)",
            0.0, 1.0, 0.25, 0.05,
            help="Higher values indicate increasing absenteeism over time"
        )
        
        # Visual indicator for absenteeism
        absent_color = "#ef4444" if absenteeism_trend > 0.6 else ("#fbbf24" if absenteeism_trend > 0.3 else "#10b981")
        absent_label = "High Concern" if absenteeism_trend > 0.6 else ("Moderate Concern" if absenteeism_trend > 0.3 else "Good")
        st.markdown(f"<p style='color: {absent_color}; font-weight: 600;'>Status: {absent_label}</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        input_values = [
            sem1_grade, sem1_approved, sem2_grade, sem2_approved,
            grade_delta, approved_delta, efficiency_change,
            absenteeism_trend, financial_stress, age_group,
            admission_grade, unemployment, prev_qual, course, attendance
        ]
    
    else:
        # Manual input mode
        st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>✏️ Manual Feature Entry</p>", unsafe_allow_html=True)
        st.markdown("<div class='info-box'>Enter all 15 features manually. Use this mode if you have pre-calculated values.</div>", unsafe_allow_html=True)
        
        input_values = []
        cols = st.columns(3)
        defaults = [12.5,5,11.8,4,-0.7,-1,-0.167,0.25,0.35,1,125.0,10.5,1,9238,1]
        
        for i, (feat, default) in enumerate(zip(feature_names, defaults)):
            with cols[i%3]:
                input_values.append(st.number_input(
                    feat.replace('_', ' ').title(), 
                    value=float(default), 
                    step=0.1 if isinstance(default, float) else 1,
                    format="%.3f" if isinstance(default, float) else "%d",
                    key=f"m{i}"
                ))
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Prediction button
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔮 Generate Prediction & Analysis", type="primary", use_container_width=True):
        with st.spinner("🔄 Analyzing student data with advanced ML algorithms..."):
            prediction, probs = get_prediction(input_values)
            dropout_prob = probs[1] * 100
            graduate_prob = probs[0] * 100
            
            # Risk status card
            st.markdown("<br>", unsafe_allow_html=True)
            
            if prediction == 1:
                st.markdown(f"""
                <div class='risk-high'>
                    <h2 style='color:white; margin:0; font-size: 1.8rem; font-weight: 700;'>⚠️ HIGH DROPOUT RISK DETECTED</h2>
                    <h1 style='font-size:4.5rem; margin:20px 0; color:white; font-weight: 800;'>{dropout_prob:.1f}%</h1>
                    <p style='font-size:1.2rem; margin:0; color:white; opacity: 0.95;'>Immediate intervention and support recommended</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='risk-low'>
                    <h2 style='color:white; margin:0; font-size: 1.8rem; font-weight: 700;'>✅ LOW DROPOUT RISK</h2>
                    <h1 style='font-size:4.5rem; margin:20px 0; color:white; font-weight: 800;'>{graduate_prob:.1f}%</h1>
                    <p style='font-size:1.2rem; margin:0; color:white; opacity: 0.95;'>Student on track for successful graduation</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Metrics summary
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Prediction", "🔴 Dropout" if prediction==1 else "🟢 Graduate")
            col_m2.metric("Dropout Probability", f"{dropout_prob:.1f}%")
            col_m3.metric("Graduate Probability", f"{graduate_prob:.1f}%")
            col_m4.metric("Confidence Level", f"{max(dropout_prob, graduate_prob):.1f}%")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Analysis tabs
            shap_vals = get_shap_values(input_values)
            top_factors = pd.DataFrame({
                'feature': feature_names,
                'value': input_values,
                'shap': shap_vals
            }).sort_values('shap', key=abs, ascending=False).head(3)
            
            tab1, tab2, tab3 = st.tabs(["📊 Probability Visualization", "🔬 SHAP Feature Analysis", "🤖 AI-Generated Insights"])
            
            with tab1:
                st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
                st.plotly_chart(plot_probability_gauge(probs), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with tab2:
                st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
                st.markdown("#### 🎯 Top 3 Contributing Factors")
                
                for idx, (i, row) in enumerate(top_factors.iterrows(), 1):
                    impact = "Increases" if row['shap'] > 0 else "Decreases"
                    impact_color = "#ef4444" if row['shap'] > 0 else "#10b981"
                    impact_icon = "⬆️" if row['shap'] > 0 else "⬇️"
                    
                    with st.expander(f"**{idx}. {row['feature'].replace('_', ' ').title()}** {impact_icon}", expanded=(idx==1)):
                        col_a, col_b = st.columns([1, 2])
                        
                        with col_a:
                            st.metric("Feature Value", f"{row['value']:.2f}")
                            st.metric("SHAP Impact", f"{row['shap']:.4f}")
                        
                        with col_b:
                            st.markdown(f"<p style='color: {impact_color}; font-weight: 600; font-size: 1.1rem;'>{impact} dropout risk by {abs(row['shap']):.4f}</p>", unsafe_allow_html=True)
                            st.info(f"This feature {'pushes the prediction toward dropout' if row['shap'] > 0 else 'protects against dropout risk'} based on the value of {row['value']:.2f}")
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
                st.plotly_chart(plot_shap_waterfall(shap_vals, input_values), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with tab3:
                st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
                st.markdown("#### 🤖 AI-Powered Explanation")
                
                with st.spinner("Generating comprehensive analysis with NVIDIA AI..."):
                    explanation = get_ai_explanation(input_values, prediction, probs, top_factors)
                
                st.markdown(f"<div class='info-box' style='font-size: 1.05rem; line-height: 1.8;'>{explanation}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: BULK PREDICTION
# ============================================================================

def page_bulk_prediction():
    st.markdown("<h1 class='main-header'>Batch Student Risk Assessment</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Process multiple students simultaneously for comprehensive cohort analysis</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='info-box'>📋 <strong>Required Format:</strong> CSV file with 15 columns: " + ", ".join(feature_names[:3]) + "... and 12 more (see template)</div>", unsafe_allow_html=True)
    
    # Input method selection
    st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
    method = st.radio("Select Input Method", ["📁 Upload CSV File", "📋 Paste CSV Data"])
    st.markdown("</div>", unsafe_allow_html=True)
    
    batch_data = None
    
    if "Upload" in method:
        st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
        file = st.file_uploader(
            "Drop your CSV file here or click to browse",
            type=['csv'],
            help="CSV must have 15 columns matching the feature order"
        )
        
        if file:
            batch_data = pd.read_csv(file)
            st.success(f"✅ Successfully loaded **{len(batch_data)} students** from file")
                else:
            show_empty_state(
                "📁",
                "No File Uploaded Yet",
                "Upload a CSV file with student data to begin batch prediction analysis. The file should contain 15 columns matching the feature template.",
                "Click 'Download Sample Template' below to see the correct format"
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
        data = st.text_area(
            "Paste CSV data below (one student per line, comma-separated)",
            height=200,
            placeholder="12.5,5,11.8,4,-0.7,-1,-0.167,0.25,0.35,1,125.0,10.5,1,9238,1
..."
        )
        
        if data:
            batch_data = pd.read_csv(io.StringIO(data), header=None, names=feature_names)
            st.success(f"✅ Successfully parsed **{len(batch_data)} students** from input")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Download template section
    with st.expander("📥 Download Sample Template & Instructions"):
        st.markdown("Download a pre-formatted template with example data to get started quickly.")
        
        template_df = pd.DataFrame(columns=feature_names)
        template_df.loc[0] = [12.5,5,11.8,4,-0.7,-1,-0.167,0.25,0.35,1,125.0,10.5,1,9238,1]
        template_df.loc[1] = [15.2,6,14.8,6,-0.4,0,0.0,0.15,0.2,0,145.0,8.5,1,9238,1]
        
        csv_buffer = io.StringIO()
        template_df.to_csv(csv_buffer, index=False)
        
        st.download_button(
            "📄 Download Template CSV",
            csv_buffer.getvalue(),
            file_name="student_template.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.dataframe(template_df, use_container_width=True)
    
    # Process predictions
    if batch_data is not None and not batch_data.empty:
        if list(batch_data.columns) == feature_names:
            if st.button("🚀 Run Batch Predictions", type="primary", use_container_width=True):
                with st.spinner(f"⚙️ Processing {len(batch_data)} students..."):
                    scaled = scaler.transform(batch_data)
                    preds = model.predict(scaled)
                    probs = model.predict_proba(scaled)
                    
                    results = batch_data.copy()
                    results['prediction'] = preds
                    results['dropout_prob'] = probs[:,1] * 100
                    results['graduate_prob'] = probs[:,0] * 100
                    results['risk_level'] = pd.cut(
                        results['dropout_prob'],
                        bins=[0,30,70,100],
                        labels=['Low','Medium','High']
                    )
                    
                    st.success("✅ Predictions completed successfully!")
                    
                    # Summary metrics
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
                    st.markdown("<p class='section-title'>📊 Summary Statistics</p>", unsafe_allow_html=True)
                    
                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                    
                    total = len(results)
                    dropouts = (preds==1).sum()
                    high_risk = (results['dropout_prob']>70).sum()
                    avg_prob = results['dropout_prob'].mean()
                    
                    col_s1.metric("Total Students", total)
                    col_s2.metric("Predicted Dropouts", f"{dropouts} ({dropouts/total*100:.1f}%)")
                    col_s3.metric("High Risk (>70%)", f"{high_risk} ({high_risk/total*100:.1f}%)")
                    col_s4.metric("Avg Dropout Probability", f"{avg_prob:.1f}%")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Visualizations
                    st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
                    st.markdown("<p class='section-title'>📈 Visual Analysis</p>", unsafe_allow_html=True)
                    
                    viz_col1, viz_col2 = st.columns(2, gap="large")
                    
                    with viz_col1:
                        st.plotly_chart(plot_risk_distribution(results), use_container_width=True)
                    
                    with viz_col2:
                        st.plotly_chart(plot_probability_histogram(results), use_container_width=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Results table
                    st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
                    st.markdown("<p class='section-title'>📋 Detailed Results</p>", unsafe_allow_html=True)
                    
                    # Filters
                    filter_col1, filter_col2 = st.columns([1, 3])
                    
                    with filter_col1:
                        risk_filter = st.multiselect(
                            "Filter by Risk Level",
                            options=['Low', 'Medium', 'High'],
                            default=['Low', 'Medium', 'High']
                        )
                    
                    with filter_col2:
                        prob_range = st.slider(
                            "Filter by Dropout Probability Range (%)",
                            0.0, 100.0, (0.0, 100.0),
                            step=5.0
                        )
                    
                    filtered = results[
                        (results['risk_level'].isin(risk_filter)) &
                        (results['dropout_prob'] >= prob_range[0]) &
                        (results['dropout_prob'] <= prob_range[1])
                    ].sort_values('dropout_prob', ascending=False).reset_index(drop=True)
                    
                    st.markdown(f"**Showing {len(filtered)} of {len(results)} students**")
                    
                    # Display with styling
                    display_cols = ['prediction', 'dropout_prob', 'graduate_prob', 'risk_level'] + feature_names[:5]
                    display_df = filtered[display_cols].copy()
                    display_df['prediction'] = display_df['prediction'].map({1: '🔴 Dropout', 0: '🟢 Graduate'})
                    
                    st.dataframe(
                        display_df.style.background_gradient(subset=['dropout_prob'], cmap='RdYlGn_r')
                                       .format({'dropout_prob': '{:.1f}%', 'graduate_prob': '{:.1f}%'}),
                        use_container_width=True,
                        height=400
                    )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # High risk students
                    high_risk_students = results[results['dropout_prob'] > 70].sort_values('dropout_prob', ascending=False)
                    
                    if not high_risk_students.empty:
                        st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
                        st.markdown("<p class='section-title'>⚠️ High-Risk Students Requiring Immediate Attention</p>", unsafe_allow_html=True)
                        st.markdown(f"<div class='warning-box'><strong>{len(high_risk_students)} students</strong> have dropout probability exceeding 70%. Priority intervention recommended.</div>", unsafe_allow_html=True)
                        
                        high_risk_display = high_risk_students[['dropout_prob', 'graduate_prob'] + feature_names[:8]].reset_index(drop=True)
                        high_risk_display.index = high_risk_display.index + 1
                        high_risk_display.index.name = 'Priority #'
                        
                        st.dataframe(
                            high_risk_display.style.background_gradient(subset=['dropout_prob'], cmap='Reds')
                                                   .format({'dropout_prob': '{:.1f}%', 'graduate_prob': '{:.1f}%'}),
                            use_container_width=True
                        )
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Download section
                    st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
                    st.markdown("<p class='section-title'>💾 Export Results</p>", unsafe_allow_html=True)
                    
                    csv = results.to_csv(index=False)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    col_dl1, col_dl2 = st.columns(2)
                    
                    with col_dl1:
                        st.download_button(
                            "📥 Download Complete Results",
                            csv,
                            file_name=f"predictions_{timestamp}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col_dl2:
                        if not high_risk_students.empty:
                            high_risk_csv = high_risk_students.to_csv(index=False)
                            st.download_button(
                                "⚠️ Download High-Risk Students Only",
                                high_risk_csv,
                                file_name=f"high_risk_{timestamp}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error(f"❌ Column mismatch! Expected {len(feature_names)} columns matching the template format.")

# ============================================================================
# PAGE: ANALYTICS DASHBOARD
# ============================================================================

def page_analytics():
    st.markdown("<h1 class='main-header'>Model Performance Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Comprehensive insights into model metrics, feature importance, and configurations</p>", unsafe_allow_html=True)
    
    # Model overview
    st.markdown("<div class='success-box'><strong>🎯 Random Forest Classifier</strong> achieving <strong>88.43% accuracy</strong> on 3,318 training samples with 15 carefully engineered features</div>", unsafe_allow_html=True)
    
    # Performance metrics
    st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>📊 Performance Metrics</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        metrics = pd.DataFrame({
            'Metric': ['Accuracy','Precision','Recall','F1-Score','ROC-AUC'],
            'Score': [88.43, 83.46, 78.17, 81.18, 93.43]
        })
        
        fig = px.bar(
            metrics, x='Metric', y='Score',
            title="Model Performance Metrics (%)",
            text='Score',
            color='Score',
            color_continuous_scale='Blues'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(
            height=400,
            yaxis_range=[0, 100],
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Arial, sans-serif'},
            title={'font': {'size': 18, 'color': '#1e293b'}}
        )
        fig.update_xaxis(gridcolor='#f1f5f9')
        fig.update_yaxis(gridcolor='#f1f5f9')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📈 Metric Interpretations")
        
        metric_descriptions = {
            'Accuracy': ('Overall correctness of predictions', 88.43, '#10b981'),
            'Precision': ('Accuracy in identifying actual dropouts', 83.46, '#3b82f6'),
            'Recall': ('Ability to catch all dropout cases', 78.17, '#8b5cf6'),
            'F1-Score': ('Harmonic mean of precision and recall', 81.18, '#ec4899'),
            'ROC-AUC': ('Model discrimination capability', 93.43, '#f59e0b')
        }
        
        for metric, (desc, score, color) in metric_descriptions.items():
            st.markdown(f"""
            <div style='background: white; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid {color};'>
                <strong style='color: {color};'>{metric}:</strong> {score:.2f}%<br>
                <small style='color: #64748b;'>{desc}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Feature importance
    st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>🔍 Global Feature Importance Analysis</p>", unsafe_allow_html=True)
    st.markdown("<div class='info-box'>Features ranked by their average impact across all predictions in the training dataset</div>", unsafe_allow_html=True)
    
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    fig = px.bar(
        importance_df, x='Importance', y='Feature', orientation='h',
        title="Feature Importance Rankings",
        color='Importance',
        color_continuous_scale='Viridis',
        text='Importance'
    )
    fig.update_traces(texttemplate='%{text:.4f}', textposition='outside')
    fig.update_layout(
        height=600,
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Arial, sans-serif'},
        title={'font': {'size': 18, 'color': '#1e293b'}},
        showlegend=False
    )
    fig.update_xaxis(gridcolor='#f1f5f9')
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Model configuration
    st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>⚙️ Model Configuration & Technical Details</p>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("""
        <div class='metric-card'>
            <h4 style='color: #667eea; margin-bottom: 0.5rem;'>🤖 Model Architecture</h4>
            <ul style='list-style: none; padding-left: 0; color: #1e293b;'>
                <li><strong>Algorithm:</strong> Random Forest</li>
                <li><strong>Trees:</strong> 300</li>
                <li><strong>Max Depth:</strong> 10</li>
                <li><strong>Class Weight:</strong> Balanced</li>
                <li><strong>Random State:</strong> 42</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown("""
        <div class='metric-card'>
            <h4 style='color: #667eea; margin-bottom: 0.5rem;'>📚 Training Dataset</h4>
            <ul style='list-style: none; padding-left: 0; color: #1e293b;'>
                <li><strong>Total Samples:</strong> 4,424</li>
                <li><strong>Training Set:</strong> 3,318 (75%)</li>
                <li><strong>Test Set:</strong> 1,106 (25%)</li>
                <li><strong>Features:</strong> 15</li>
                <li><strong>Scaling:</strong> StandardScaler</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_c:
        st.markdown("""
        <div class='metric-card'>
            <h4 style='color: #667eea; margin-bottom: 0.5rem;'>👥 Age Group Encoding</h4>
            <ul style='list-style: none; padding-left: 0; color: #1e293b;'>
                <li><strong>Group 0:</strong> 17-20 years</li>
                <li><strong>Group 1:</strong> 21-25 years</li>
                <li><strong>Group 2:</strong> 26+ years</li>
                <li style='margin-top: 0.5rem;'><em style='color: #64748b; font-size: 0.85rem;'>Mature students show higher risk patterns</em></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Data quality section
    st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>✅ Data Quality & Preprocessing Pipeline</p>", unsafe_allow_html=True)
    
    col_dq1, col_dq2 = st.columns(2, gap="large")
    
    with col_dq1:
        st.markdown("""
        <div class='success-box'>
            <h4 style='margin-top: 0;'>Preprocessing Steps</h4>
            <ol style='color: #1b5e20; line-height: 1.8;'>
                <li><strong>Data Leakage Prevention:</strong> Removed target-derived columns</li>
                <li><strong>Feature Engineering:</strong> Calculated performance deltas</li>
                <li><strong>Encoding:</strong> Categorical variables transformed</li>
                <li><strong>Normalization:</strong> StandardScaler applied</li>
                <li><strong>Train-Test Split:</strong> 75/25 stratified split</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col_dq2:
        st.markdown("""
        <div class='info-box'>
            <h4 style='margin-top: 0;'>Engineered Features</h4>
            <ul style='color: #0d47a1; line-height: 1.8;'>
                <li><strong>grade_delta:</strong> Performance trend (sem2 - sem1)</li>
                <li><strong>approved_delta:</strong> Course completion trend</li>
                <li><strong>efficiency_change:</strong> Approval rate dynamics</li>
                <li><strong>financial_stress_index:</strong> Composite financial risk</li>
                <li><strong>age_group:</strong> Categorical age buckets</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown("<h2 style='color: white; text-align: center; margin-bottom: 2rem;'>🎓 Navigation</h2>", unsafe_allow_html=True)
        
        page = st.radio(
            "",
            ["🎯 Individual Assessment", "📦 Batch Processing", "📊 Analytics Dashboard"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.1); padding: 1.5rem; border-radius: 12px; backdrop-filter: blur(10px);'>
            <h3 style='margin-top: 0; color: white;'>ℹ️ About</h3>
            <p style='color: rgba(255, 255, 255, 0.9); font-size: 0.9rem; line-height: 1.6;'>
                <strong>Student Dropout Predictor</strong><br><br>
                AI-powered early warning system with:
            </p>
            <ul style='color: rgba(255, 255, 255, 0.85); font-size: 0.85rem; line-height: 1.8;'>
                <li>SHAP explainable AI</li>
                <li>NVIDIA NIM integration</li>
                <li>88.43% prediction accuracy</li>
                <li>Real-time risk assessment</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.1); padding: 1.5rem; border-radius: 12px;'>
            <h3 style='margin-top: 0; color: white;'>📈 Model Statistics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col_s1, col_s2 = st.columns(2)
        col_s1.metric("Accuracy", "88.43%", delta="High", delta_color="off")
        col_s2.metric("ROC-AUC", "93.43%", delta="Excellent", delta_color="off")
        col_s1.metric("Trees", "300", delta="Ensemble", delta_color="off")
        col_s2.metric("Features", "15", delta="Optimized", delta_color="off")
        
        st.markdown("---")
        
        st.markdown("""
        <p style='text-align: center; color: rgba(255, 255, 255, 0.6); font-size: 0.75rem; margin-top: 2rem;'>
            Powered by Databricks ML & NVIDIA NIM<br>
            v2.0 | Production Ready
        </p>
        """, unsafe_allow_html=True)
    
        
    # Display welcome tutorial for first-time users
    if st.session_state.show_tutorial:
        show_welcome_tutorial()
        st.divider()
    
    # Route to pages
    if "Individual" in page:
        page_single_prediction()
    elif "Batch" in page:
        page_bulk_prediction()
    else:
        page_analytics()

if __name__ == "__main__":
    main()
