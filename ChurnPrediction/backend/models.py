from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(50), index=True)
    churn_probability = Column(Float)
    churn_prediction = Column(String(10))
    expected_value = Column(Float)
    predicted_at = Column(DateTime, default=datetime.utcnow)
    prediction_type = Column(String(10))  # single/csv