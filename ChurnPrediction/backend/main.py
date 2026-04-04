#main file for backend running and endpoint definition
#run this file while in backed directory
import io
import pandas as pd
import pickle
import joblib
from fastapi import FastAPI,UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()
# Load the trained model

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
#enalbe CORS for all origins, methods, and headers

model = joblib.load('churn_model.pkl')
# Define the input data model

FEATURES = [
    "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
    "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
    "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
    "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod",
    "MonthlyCharges", "TotalCharges"
]
# get endpoint of home page 
@app.get("/")
def root():
    return {"message": "Churn API is running"}
# endpoint for single prediction
@app.post("/predict/single")
def predict_single(data: dict):
    df = pd.DataFrame([data])
    prob = model.predict_proba(df)[0][1]
    return {
        "churn_probability": round(prob * 100, 2),
        "churn_prediction": "Yes" if prob > 0.5 else "No"
    }
# endpoint for csv prediction
@app.post("/predict/bulk")
async def predict_bulk(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    
    probs = model.predict_proba(df[FEATURES])[:, 1]
    df["churn_prob"] = probs
    df["churn_pred"] = df["churn_prob"].apply(lambda x: "Yes" if x > 0.5 else "No")
    df["rank"] = df["churn_prob"].rank(ascending=False).astype(int)
    df = df.sort_values("rank")
    
    return df.to_dict(orient="records")