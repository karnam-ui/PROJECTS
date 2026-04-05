#main file for backend running and endpoint definition
#run this file while in backed directory
from fastapi import Request

from fastapi import HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from auth import get_token_from_header
from auth import create_token, decode_token, hash_password, verify_password
from database import Base, engine,get_db
from models import Prediction
from sqlalchemy.orm import Session
from fastapi import Depends
import io
import pandas as pd

import joblib
from fastapi import FastAPI,UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from users import User
from schemas import UserRegister, UserLogin, Token
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


app = FastAPI()
# Load the trained model

limiter = Limiter(key_func=get_remote_address)#get ip address for rate limiting
app.state.limiter = limiter#add limiter to app state

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "message": "Too many requests. Please slow down."
        }
    )

#basic error handling

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Invalid input data",
            "details": str(exc)
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc)
        }
    )

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
@limiter.limit("10/minute")
def get_predictions(request = Request,db: Session = Depends(get_db), token_data: dict = Depends(get_token_from_header)):
    return db.query(Prediction).all()

# endpoint for single prediction
@app.post("/predict/single")
@limiter.limit("10/minute")
def predict_single( request : Request, data: dict, db: Session = Depends(get_db), token_data: dict = Depends(get_token_from_header)):
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
@limiter.limit("10/minute")
async def predict_bulk(request : Request,file: UploadFile = File(...), db: Session = Depends(get_db), token_data: dict = Depends(get_token_from_header)):
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
        )
        db.add(prediction)
    
    db.commit()
    return df.to_dict(orient="records")

#end point for register user
@app.post("/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}
#end point for login user
@app.post("/login", response_model=Token)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

