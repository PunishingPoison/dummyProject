# Student Dropout Predictor

An AI-powered early warning system that predicts student dropout risk using a Random Forest classifier. The model achieves 88.43% accuracy with SHAP explainability, providing actionable insights into the factors driving each prediction.

Built with a Next.js 15 frontend and a Python FastAPI backend. The machine learning model was trained on 3,318 student records from the Open University Learning Analytics Dataset (OULAD).

---

## Features

- **Single Risk Assessment** — Enter student data through an intuitive smart form with auto-calculated trends, or use manual mode for direct feature entry. Get instant predictions with SHAP explanations.
- **Batch Processing** — Upload a CSV file or paste data to analyze multiple students at once, with cohort-level statistics and risk distribution visualizations.
- **Analytics Dashboard** — View model performance metrics, feature importance rankings, and model configuration details.
- **SHAP Explainability** — Understand which factors contribute to each prediction with interactive waterfall charts and top-factors breakdowns.
- **Probability Gauge** — Visual risk indicator with color-coded thresholds (green = low, amber = moderate, red = high).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS v4 |
| Backend | Python 3.12+, FastAPI, Uvicorn |
| Machine Learning | scikit-learn 1.6.1 (Random Forest), SHAP, pandas, numpy |
| Charts | Recharts |
| Icons | Lucide React |

---

## Prerequisites

- **Node.js** >= 18.17.0
- **Python** >= 3.12
- **npm** or **yarn**
- **Git** (optional, for cloning)

---

## Local Setup

### 1. Clone the repository

```
git clone https://github.com/PunishingPoison/dummyProject.git
cd HackBricks-Project-master
```

### 2. Backend setup

```
cd backend
python -m pip install -r requirements.txt
cd ..
```

This installs FastAPI, uvicorn, scikit-learn, SHAP, pandas, numpy, and other dependencies.

### 3. Frontend setup

```
npm install
```

### 4. Start the application

Run both the backend and frontend simultaneously:

```
npm run dev:all
```

This starts:
- Backend at `http://localhost:8000` (FastAPI + Uvicorn)
- Frontend at `http://localhost:4000` (Next.js dev server)

Alternatively, start them in separate terminals:

```
# Terminal 1 - Backend
cd backend && python -m uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
npm run dev -- --port 4000
```

### 5. Open the application

Visit **http://localhost:4000** in your browser.

---

## Usage

### Single Prediction

1. Navigate to the **Predict** page.
2. Choose **Smart Input** mode (recommended) or **Manual Input**.
3. Fill in the form across four sections: Academic, Demographics, Financial, and Risk Factors.
4. Click **Generate Prediction**.
5. View the result with:
   - Risk card showing the predicted outcome and confidence.
   - Probability gauge for visual risk assessment.
   - SHAP waterfall chart showing feature contributions.
   - Top factors breakdown with directional impact.

### Batch Processing

1. Navigate to the **Batch** page.
2. Upload a CSV file or paste comma-separated data.
3. Each row should contain 15 feature values in the correct order.
4. Click **Run Predictions**.
5. View cohort summaries, distribution charts, and export results by risk level.

### Analytics

1. Navigate to the **Analytics** page.
2. View model metrics, feature importance bar chart, and configuration details.
3. Explore the engineered features and preprocessing steps.

---

## Project Structure

```
backend/
  main.py                          FastAPI server with prediction endpoints
  requirements.txt                 Python dependencies
  random_forest_dropout_model.pkl  Trained Random Forest model
  scaler.pkl                       Fitted StandardScaler
  feature_names.pkl                Feature names list
src/
  app/
    page.tsx                       Landing page
    layout.tsx                     Root layout with metadata
    globals.css                    Global styles and Tailwind imports
    predict/page.tsx               Single prediction page with smart/manual input
    batch/page.tsx                 Batch CSV processing page
    analytics/page.tsx             Model analytics dashboard
  components/
    Navbar.tsx                     Top navigation bar
    RiskCard.tsx                   Prediction result card
    MetricCard.tsx                 Stat display card
    GaugeChart.tsx                 Probability gauge visualization
    ShapWaterfall.tsx              SHAP waterfall bar chart
    RiskDistributionPie.tsx        Risk level distribution pie chart
    ProbabilityHistogram.tsx       Probability distribution histogram
    FeatureImportance.tsx          Global feature importance chart
    EmptyState.tsx                 Empty state placeholder
  lib/
    api.ts                         API client functions
    types.ts                       TypeScript types and helper functions
public/
    sample_data.csv                Sample CSV for batch upload
next.config.js                     Next.js configuration with API rewrites
package.json                       Node.js dependencies and scripts
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/predict` | Single prediction (accepts `{ features: [15 floats] }`) |
| POST | `/api/predict/batch` | Batch prediction via CSV file upload |
| GET | `/api/analytics` | Model metrics, feature importance, and config |

In development, the frontend proxies `/api/*` requests to `localhost:8000/api/*` via Next.js rewrites (configured in `next.config.js`).

---

## Model Details

| Property | Value |
|---|---|
| Algorithm | Random Forest |
| Trees | 300 |
| Max Depth | 10 |
| Class Weight | Balanced |
| Total Samples | 4,424 |
| Training Set | 3,318 (75%) |
| Test Set | 1,106 (25%) |
| Features | 15 |
| Accuracy | 88.43% |
| ROC-AUC | 93.43% |

The model was trained on the Open University Learning Analytics Dataset (OULAD). It uses 15 features spanning academic performance, demographics, financial indicators, and behavioral patterns.

---

## Engineered Features

- **grade_delta** — Change in average grade between semester 1 and 2 (positive = improving).
- **approved_delta** — Change in number of approved courses between semesters.
- **efficiency_change** — Change in approval rate (approved/enrolled) between semesters.
- **financial_stress_index** — Composite score from debt status, tuition payment, and scholarship status.
- **age_group** — Categorical age buckets (17-20, 21-25, 26+).

---

## License

This project is submitted for hackathon evaluation. All rights reserved.
