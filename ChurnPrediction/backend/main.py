#main file for backend running and endpoint definition
#run this file while in backed directory
from database import Base, engine,get_db
from models import Prediction
from sqlalchemy.orm import Session
from fastapi import Depends
import io
import pandas as pd
import pickle
import joblib
from fastapi import FastAPI,UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()
# Load the trained model

Base.metadata.create_all(bind=engine)  # Create tables if they don't exist

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

@app.get("/predictions")
def get_predictions(db: Session = Depends(get_db)):
    return db.query(Prediction).all()

# endpoint for single prediction
@app.post("/predict/single")
def predict_single(data: dict, db: Session = Depends(get_db)):
    df = pd.DataFrame([data])
    prob = model.predict_proba(df)[0][1]
    
    prediction = Prediction(
        customer_id=data.get("customerID", "unknown"),
        churn_probability=prob,
        churn_prediction="Yes" if prob > 0.5 else "No",
        expected_value=prob * df["MonthlyCharges"].iloc[0] * 12,
        prediction_type="single"
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return {
        "id": prediction.id,
        "customer_id": prediction.customer_id,
        "churn_probability": round(prob * 100, 2),
        "churn_prediction": "Yes" if prob > 0.5 else "No",
        "expected_value": round(prob * df["MonthlyCharges"].iloc[0] * 12, 2),
        "prediction_time": prediction.predicted_at,
        "prediction_type": "single"
    }

# endpoint for csv prediction
@app.post("/predict/bulk")
async def predict_bulk(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(0)
    
    probs = model.predict_proba(df[FEATURES])[:, 1]
    df["churn_prob"] = probs
    df["churn_pred"] = df["churn_prob"].apply(lambda x: "Yes" if x > 0.5 else "No")
    df["rank"] = df["churn_prob"].rank(ascending=False).astype(int)
    df = df.sort_values("rank")
    
    for _, row in df.iterrows():
        prediction = Prediction(
            id = row["rank"],
            customer_id=row.get("customerID", "unknown"),
            churn_probability=round(row["churn_prob"] * 100, 2),
            churn_prediction=row["churn_pred"],
            expected_value=round(row["churn_prob"] * row["MonthlyCharges"] * 12, 2),
            prediction_type="bulk",
            prediction_time=row.get("predicted_at", pd.Timestamp.now())

        )
        db.add(prediction)
    
    db.commit()
    return df.to_dict(orient="records")

if __name__ == "__main__":
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

