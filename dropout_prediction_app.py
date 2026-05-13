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

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {font-size: 2.8rem; font-weight: 700; color: #1f77b4; margin-bottom: 0.5rem; text-align: center;}
    .sub-header {font-size: 1.3rem; color: #666; margin-bottom: 2rem; text-align: center;}
    .risk-high {background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; border-radius: 15px; text-align: center;}
    .risk-low {background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; border-radius: 15px; text-align: center;}
    .info-box {background: #f8f9fa; border-left: 4px solid #1f77b4; padding: 15px; border-radius: 5px; margin: 10px 0;}
    .warning-box {background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 10px 0;}
    .success-box {background: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; margin: 10px 0;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {background-color: #f0f2f6; border-radius: 6px 6px 0 0; padding: 10px 20px;}
    .stTabs [aria-selected="true"] {background-color: #1f77b4; color: white;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD MODEL AND RESOURCES
# ============================================================================
@st.cache_resource
def load_resources():
    """Load model, scaler, feature names, and initialize SHAP explainer"""
    try:
        base_path = '/Workspace/Users/vcmohitrao@gmail.com/Drafts/HackBricks-Project/'
        
        with open(base_path + 'random_forest_dropout_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open(base_path + 'scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        with open(base_path + 'feature_names.pkl', 'rb') as f:
            feature_names = pickle.load(f)
        
        explainer = shap.TreeExplainer(model)
        
        try:
            api_key = os.getenv("NVIDIA_API_KEY", "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")
            client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)
        except:
            client = None
        
        return model, scaler, feature_names, explainer, client
    except Exception as e:
        st.error(f"❌ Error loading resources: {str(e)}")
        st.stop()

model, scaler, feature_names, explainer, nim_client = load_resources()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def calculate_deltas(sem1_grade, sem1_approved, sem1_enrolled, sem2_grade, sem2_approved, sem2_enrolled):
    grade_delta = sem2_grade - sem1_grade
    approved_delta = sem2_approved - sem1_approved
    if sem1_enrolled > 0 and sem2_enrolled > 0:
        efficiency_change = (sem2_approved/sem2_enrolled) - (sem1_approved/sem1_enrolled)
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
        return "⚠️ NVIDIA NIM API not configured."
    
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
    except:
        return "⚠️ Could not generate AI explanation."

# ============================================================================
# VISUALIZATIONS
# ============================================================================
def plot_probability_gauge(probabilities):
    dropout_prob = probabilities[1] * 100
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dropout_prob,
        title={'text': "Dropout Probability (%)", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': '#90EE90'},
                {'range': [30, 70], 'color': '#FFD700'},
                {'range': [70, 100], 'color': '#FF6B6B'}
            ]
        }
    ))
    fig.update_layout(height=350)
    return fig

def plot_shap_waterfall(shap_values, input_values):
    df = pd.DataFrame({
        'feature': feature_names,
        'shap': shap_values
    }).sort_values('shap', key=abs, ascending=False).head(10)
    
    colors = ['#FF6B6B' if x > 0 else '#90EE90' for x in df['shap']]
    fig = go.Figure(go.Bar(y=df['feature'], x=df['shap'], orientation='h', marker=dict(color=colors)))
    fig.update_layout(title="SHAP Feature Impacts", height=500, yaxis={'categoryorder': 'total ascending'})
    return fig

def plot_risk_distribution(results_df):
    risk_cat = pd.cut(results_df['dropout_prob'], bins=[0,30,70,100], 
                      labels=['Low (<30%)', 'Medium (30-70%)', 'High (>70%)'])
    counts = risk_cat.value_counts()
    fig = px.pie(values=counts.values, names=counts.index, title="Risk Distribution")
    fig.update_layout(height=400)
    return fig

def plot_probability_histogram(results_df):
    fig = px.histogram(results_df, x='dropout_prob', nbins=20, title="Dropout Probability Distribution")
    fig.add_vline(x=30, line_dash="dash", line_color="green")
    fig.add_vline(x=70, line_dash="dash", line_color="red")
    return fig

# ============================================================================
# PAGES
# ============================================================================
def page_single_prediction():
    st.markdown("<h1 class='main-header'>🎓 Single Student Prediction</h1>", unsafe_allow_html=True)
    
    input_mode = st.radio("Input Method", ["📊 Smart Input", "📝 Manual Input"])
    
    if "Smart" in input_mode:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🟦 Semester 1")
            sem1_grade = st.number_input("Grade", 0.0, 20.0, 12.5, 0.1, key="s1g")
            sem1_approved = st.number_input("Approved", 0, 30, 5, key="s1a")
            sem1_enrolled = st.number_input("Enrolled", 0, 30, 6, key="s1e")
        with col2:
            st.markdown("#### 🟩 Semester 2")
            sem2_grade = st.number_input("Grade", 0.0, 20.0, 11.8, 0.1, key="s2g")
            sem2_approved = st.number_input("Approved", 0, 30, 4, key="s2a")
            sem2_enrolled = st.number_input("Enrolled", 0, 30, 6, key="s2e")
        
        grade_delta, approved_delta, efficiency_change = calculate_deltas(
            sem1_grade, sem1_approved, sem1_enrolled, sem2_grade, sem2_approved, sem2_enrolled)
        
        st.markdown("### 📈 Calculated Trends")
        c1, c2, c3 = st.columns(3)
        c1.metric("Grade Δ", f"{grade_delta:.2f}")
        c2.metric("Approved Δ", f"{approved_delta}")
        c3.metric("Efficiency Δ", f"{efficiency_change:.3f}")
        
        col3, col4 = st.columns(2)
        with col3:
            absenteeism_trend = st.slider("Absenteeism (0-1)", 0.0, 1.0, 0.25, 0.05)
            financial_stress = st.slider("Financial Stress (0-1)", 0.0, 1.0, 0.35, 0.05)
            age_group = st.selectbox("Age Group", [0,1,2,3], 
                                     format_func=lambda x: ["<20","20-24","25-30",">30"][x])
        with col4:
            admission_grade = st.number_input("Admission Grade", 0.0, 200.0, 125.0)
            unemployment = st.number_input("Unemployment %", 0.0, 30.0, 10.5)
            prev_qual = st.number_input("Prev Qualification", 0, 20, 1)
        
        course = st.number_input("Course Code", 0, 10000, 9238)
        attendance = st.selectbox("Attendance", [1,0], format_func=lambda x: "Day" if x==1 else "Evening")
        
        input_values = [sem1_grade, sem1_approved, sem2_grade, sem2_approved,
                       grade_delta, approved_delta, efficiency_change,
                       absenteeism_trend, financial_stress, age_group,
                       admission_grade, unemployment, prev_qual, course, attendance]
    else:
        st.markdown("### Enter 15 Features")
        input_values = []
        cols = st.columns(3)
        defaults = [12.5,5,11.8,4,-0.7,-1,-0.167,0.25,0.35,1,125.0,10.5,1,9238,1]
        for i, (feat, default) in enumerate(zip(feature_names, defaults)):
            with cols[i%3]:
                input_values.append(st.number_input(feat, value=float(default), key=f"m{i}"))
    
    if st.button("🔮 Predict", type="primary", use_container_width=True):
        prediction, probs = get_prediction(input_values)
        dropout_prob = probs[1] * 100
        
        if prediction == 1:
            st.markdown(f"""<div class='risk-high'>
                <h2 style='color:white'>🔴 HIGH RISK</h2>
                <h1 style='font-size:3rem;color:white'>{dropout_prob:.1f}%</h1>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='risk-low'>
                <h2 style='color:white'>🟢 LOW RISK</h2>
                <h1 style='font-size:3rem;color:white'>{probs[0]*100:.1f}%</h1>
            </div>""", unsafe_allow_html=True)
        
        shap_vals = get_shap_values(input_values)
        top_factors = pd.DataFrame({
            'feature': feature_names,
            'value': input_values,
            'shap': shap_vals
        }).sort_values('shap', key=abs, ascending=False).head(3)
        
        tab1, tab2, tab3 = st.tabs(["📊 Gauge", "🔬 SHAP", "🤖 AI"])
        with tab1:
            st.plotly_chart(plot_probability_gauge(probs), use_container_width=True)
        with tab2:
            st.plotly_chart(plot_shap_waterfall(shap_vals, input_values), use_container_width=True)
        with tab3:
            explanation = get_ai_explanation(input_values, prediction, probs, top_factors)
            st.markdown(f"<div class='info-box'>{explanation}</div>", unsafe_allow_html=True)

def page_bulk_prediction():
    st.markdown("<h1 class='main-header'>📦 Bulk Predictions</h1>", unsafe_allow_html=True)
    
    method = st.radio("Input Method", ["📁 Upload CSV", "📋 Paste Data"])
    batch_data = None
    
    if "Upload" in method:
        file = st.file_uploader("Upload CSV", type=['csv'])
        if file:
            batch_data = pd.read_csv(file)
            st.success(f"✅ Loaded {len(batch_data)} students")
    else:
        data = st.text_area("Paste CSV data", height=200)
        if data:
            batch_data = pd.read_csv(io.StringIO(data), header=None, names=feature_names)
            st.success(f"✅ Parsed {len(batch_data)} students")
    
    if batch_data is not None and not batch_data.empty:
        if list(batch_data.columns) == feature_names:
            if st.button("🚀 Run Predictions", type="primary"):
                scaled = scaler.transform(batch_data)
                preds = model.predict(scaled)
                probs = model.predict_proba(scaled)
                
                results = batch_data.copy()
                results['prediction'] = preds
                results['dropout_prob'] = probs[:,1] * 100
                results['risk'] = pd.cut(results['dropout_prob'], [0,30,70,100], labels=['Low','Med','High'])
                
                st.markdown("## 📊 Summary")
                c1,c2,c3 = st.columns(3)
                c1.metric("Total", len(results))
                c2.metric("Dropouts", (preds==1).sum())
                c3.metric("High Risk", (results['dropout_prob']>70).sum())
                
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(plot_risk_distribution(results), use_container_width=True)
                with col2:
                    st.plotly_chart(plot_probability_histogram(results), use_container_width=True)
                
                st.dataframe(results.sort_values('dropout_prob', ascending=False).head(20))
                
                csv = results.to_csv(index=False)
                st.download_button("📥 Download Results", csv, 
                                  f"predictions_{datetime.now():%Y%m%d_%H%M%S}.csv", "text/csv")

def page_analytics():
    st.markdown("<h1 class='main-header'>📊 Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<div class='success-box'>Random Forest: 88.43% accuracy on 3,318 students</div>", 
                unsafe_allow_html=True)
    
    metrics = pd.DataFrame({
        'Metric': ['Accuracy','Precision','Recall','F1','ROC-AUC'],
        'Score': [88.43, 83.46, 78.17, 81.18, 93.43]
    })
    fig = px.bar(metrics, x='Metric', y='Score', title="Model Performance")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Feature Importance")
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    fig = px.bar(importance_df, x='Importance', y='Feature', orientation='h')
    fig.update_layout(height=600, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# MAIN
# ============================================================================
def main():
    with st.sidebar:
        st.markdown("## 🎓 Navigation")
        page = st.radio("", ["🎯 Single", "📦 Bulk", "📊 Analytics"], label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Student Dropout Predictor**
        - 🤖 AI Explanations (NVIDIA NIM)
        - 🔬 SHAP Analysis
        - 📊 88.43% Accuracy
        """)
        
        c1,c2 = st.columns(2)
        c1.metric("Trees", "300")
        c2.metric("Features", "15")
    
    if "Single" in page:
        page_single_prediction()
    elif "Bulk" in page:
        page_bulk_prediction()
    else:
        page_analytics()

if __name__ == "__main__":
    main()
