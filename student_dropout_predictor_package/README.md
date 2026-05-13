# Student Dropout Prediction System

AI-powered system to predict student dropout risk with SHAP explanations and interactive visualizations.

## 🎯 Features

* **Single Student Prediction** - Smart input with auto-calculated deltas
* **Bulk Predictions** - Upload CSV or paste data for batch processing
* **Analytics Dashboard** - Model performance and feature importance insights
* **AI Explanations** - NVIDIA NIM integration for natural language insights
* **SHAP Visualizations** - Interactive feature importance charts

## 📦 Installation

### 1. Install Python Requirements

```bash
pip install -r requirements.txt
```

### 2. (Optional) Set NVIDIA API Key for AI Explanations

If you want to enable AI-powered explanations:

**Windows:**
```cmd
set NVIDIA_API_KEY=your_nvidia_api_key_here
```

**Mac/Linux:**
```bash
export NVIDIA_API_KEY=your_nvidia_api_key_here
```

Or create a `.env` file:
```
NVIDIA_API_KEY=your_nvidia_api_key_here
```

## 🚀 Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📁 Files Included

* `app.py` - Main Streamlit application
* `random_forest_dropout_model.pkl` - Trained Random Forest model (9.89 MB)
* `scaler.pkl` - StandardScaler for feature normalization (1.22 KB)
* `feature_names.pkl` - List of 15 feature names (0.36 KB)
* `requirements.txt` - Python dependencies
* `README.md` - This file

## 🎓 Model Information

* **Algorithm:** Random Forest Classifier
* **Trees:** 300
* **Accuracy:** 88.43%
* **ROC-AUC:** 93.43%
* **Training Data:** 3,318 students
* **Features:** 15 academic and demographic factors

## 📊 Features Used

1. Curricular_units_1st_sem_grade
2. Curricular_units_1st_sem_approved
3. Curricular_units_2nd_sem_grade
4. Curricular_units_2nd_sem_approved
5. grade_delta
6. approved_delta
7. efficiency_change
8. absenteeism_trend
9. financial_stress_index
10. age_group
11. Admission_grade
12. Unemployment_rate
13. Previous_qualification
14. Course
15. Daytime_per_evening_attendance

## 💡 Usage Tips

### Smart Input Mode
Enter semester performance data and the app automatically calculates:
* `grade_delta` - Change in grades (semester 2 - semester 1)
* `approved_delta` - Change in approved courses
* `efficiency_change` - Change in course approval rate

### Bulk Predictions
Format your CSV with 15 columns in the order shown above. No headers needed for pasted data.

### Example CSV Format
```
12.5,5,11.8,4,-0.7,-1,-0.167,0.25,0.35,1,125.0,10.5,1,9238,1
15.2,6,14.8,6,-0.4,0,0.0,0.15,0.2,0,145.0,8.5,1,9238,1
```

## 🔧 Troubleshooting

**Error loading model files:**
* Make sure all `.pkl` files are in the same directory as `app.py`

**AI explanations not working:**
* Set your NVIDIA API key as an environment variable
* The app will still work without AI explanations

**Import errors:**
* Run `pip install -r requirements.txt` to install all dependencies

## 📄 License

Educational project for student dropout prediction.

---

**Powered by:** Databricks ML, Random Forest, SHAP, NVIDIA NIM, Streamlit
