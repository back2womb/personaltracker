import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib
from sqlmodel import Session, select
from datetime import date, timedelta
import os

from app.models.task import Task
from app.models.daily_log import DailyLog
from app.core.database import engine

MODEL_PATH = "productivity_model.pkl"

def get_training_data():
    """
    Constructs a dataset of (Features) -> (Success/Fail).
    """
    with Session(engine) as session:
        tasks = session.exec(select(Task)).all()
        logs = session.exec(select(DailyLog)).all()
        
    data = []
    
    # Map logs for quick lookup: (task_id, date) -> completed
    log_map = {(l.task_id, l.log_date): l.completed for l in logs}
    
    # Generate historical data points
    # Look back 30 days
    today = date.today()
    for task in tasks:
        # For each of the last 30 days, was this task done?
        # If the task existed then? (using created_at would be better but keeping simple)
        for i in range(1, 31):
            check_date = today - timedelta(days=i)
            # If task was created after check_date, skip
            if task.created_at.date() > check_date:
                continue
                
            is_done = log_map.get((task.id, check_date), False)
            
            # Feature Extraction
            scheduled_min = 0
            try:
                if task.scheduled_time:
                    scheduled_min = int(task.scheduled_time)
            except:
                pass # Default to 0 if parsing fails
            
            data.append({
                "category": task.category or "Others",
                "scheduled_minutes": scheduled_min,
                "day_of_week": check_date.weekday(), # 0=Mon, 6=Sun
                "title_length": len(task.title),
                "is_weekend": 1 if check_date.weekday() >= 5 else 0,
                "target": 1 if is_done else 0
            })
            
    return pd.DataFrame(data)

def train_predictor_model():
    """
    Trains a Random Forest classifier.
    """
    df = get_training_data()
    
    if df.empty or len(df) < 10:
        return {"status": "error", "message": "Not enough data to train (need > 10 records)."}

    X = df.drop(columns=["target"])
    y = df["target"]
    
    # Preprocessing Pipeline
    # Category -> OneHot
    # Numerical -> Pass through (or scale, but RF is robust)
    
    categorical_features = ["category"]
    numerical_features = ["scheduled_minutes", "day_of_week", "title_length", "is_weekend"]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', SimpleImputer(strategy='constant', fill_value=0), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
        
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    model.fit(X, y)
    
    # Save Model
    joblib.dump(model, MODEL_PATH)
    
    # Calculate simple accuracy
    score = model.score(X, y)
    
    return {"status": "success", "accuracy": f"{score:.2f}", "samples": len(df)}

def predict_task_success(category: str, scheduled_minutes: int, title: str):
    """
    Predicts probability (0-100%) of completing this task today.
    """
    if not os.path.exists(MODEL_PATH):
        return None # Model not trained yet
        
    model = joblib.load(MODEL_PATH)
    
    today = date.today()
    
    input_data = pd.DataFrame([{
        "category": category,
        "scheduled_minutes": scheduled_minutes,
        "day_of_week": today.weekday(),
        "title_length": len(title),
        "is_weekend": 1 if today.weekday() >= 5 else 0
    }])
    
    # Predict Probability
    # classes_ are [0, 1] usually. We want prob of class 1.
    probs = model.predict_proba(input_data)
    success_prob = probs[0][1] # Probability of '1' (Success)
    
    return int(success_prob * 100)
