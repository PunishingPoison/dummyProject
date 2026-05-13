import os
import pickle
import io
import numpy as np
import pandas as pd
import shap
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Student Dropout Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:4000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "random_forest_dropout_model.pkl"), "rb") as f:
    model = pickle.load(f)
with open(os.path.join(BASE_DIR, "scaler.pkl"), "rb") as f:
    scaler = pickle.load(f)
with open(os.path.join(BASE_DIR, "feature_names.pkl"), "rb") as f:
    feature_names = pickle.load(f)

explainer = shap.TreeExplainer(model)

FEATURE_DISPLAY_NAMES = [
    "1st Sem Grade", "1st Sem Approved", "2nd Sem Grade", "2nd Sem Approved",
    "Grade Delta", "Approved Delta", "Efficiency Change",
    "Absenteeism Trend", "Financial Stress Index", "Age Group",
    "Admission Grade", "Unemployment Rate", "Previous Qualification",
    "Course", "Attendance"
]

class PredictRequest(BaseModel):
    features: list[float]

class PredictResponse(BaseModel):
    prediction: int
    dropout_probability: float
    graduate_probability: float
    shap_values: list[float]
    feature_names: list[str]
    feature_display_names: list[str]

def compute_shap(input_df):
    shap_values = explainer.shap_values(input_df)
    if isinstance(shap_values, list):
        shap_vals = shap_values[1][0] if shap_values[1].ndim == 2 else shap_values[1]
    elif shap_values.ndim == 3:
        shap_vals = shap_values[0, :, 1]
    elif shap_values.ndim == 2:
        shap_vals = shap_values[0]
    else:
        shap_vals = shap_values
    return np.array(shap_vals).flatten().tolist()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/analytics")
def get_analytics():
    metrics = {
        "accuracy": 88.43,
        "precision": 83.46,
        "recall": 78.17,
        "f1_score": 81.18,
        "roc_auc": 93.43,
    }
    importance = model.feature_importances_.tolist()
    config = {
        "algorithm": "Random Forest",
        "trees": 300,
        "max_depth": 10,
        "class_weight": "balanced",
        "random_state": 42,
        "total_samples": 4424,
        "training_samples": 3318,
        "test_samples": 1106,
        "features_count": 15,
        "scaling": "StandardScaler",
    }
    return {
        "metrics": metrics,
        "feature_importance": {
            "features": feature_names,
            "display_names": FEATURE_DISPLAY_NAMES,
            "values": importance,
        },
        "config": config,
    }


@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if len(req.features) != len(feature_names):
        raise HTTPException(
            status_code=400,
            detail=f"Expected {len(feature_names)} features, got {len(req.features)}",
        )
    input_df = pd.DataFrame([req.features], columns=feature_names)
    input_scaled = scaler.transform(input_df)
    pred = int(model.predict(input_scaled)[0])
    probs = model.predict_proba(input_scaled)[0]
    shap_vals = compute_shap(input_df)
    return PredictResponse(
        prediction=pred,
        dropout_probability=round(probs[1] * 100, 2),
        graduate_probability=round(probs[0] * 100, 2),
        shap_values=shap_vals,
        feature_names=feature_names,
        feature_display_names=FEATURE_DISPLAY_NAMES,
    )


@app.post("/api/predict/batch")
async def predict_batch(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception:
        try:
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")), header=None, names=feature_names)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")
    if list(df.columns) != feature_names:
        if df.shape[1] == len(feature_names):
            df.columns = feature_names
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Expected {len(feature_names)} columns, got {df.shape[1]}",
            )
    scaled = scaler.transform(df)
    preds = model.predict(scaled).tolist()
    probs = model.predict_proba(scaled)
    results = []
    for i in range(len(df)):
        results.append({
            "prediction": int(preds[i]),
            "dropout_probability": round(probs[i][1] * 100, 2),
            "graduate_probability": round(probs[i][0] * 100, 2),
        })
    total = len(df)
    dropout_count = sum(1 for r in results if r["prediction"] == 1)
    high_risk = sum(1 for r in results if r["dropout_probability"] > 70)
    avg_prob = round(np.mean([r["dropout_probability"] for r in results]), 2)
    return {
        "total": total,
        "dropout_count": dropout_count,
        "high_risk_count": high_risk,
        "avg_dropout_probability": avg_prob,
        "results": results,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
