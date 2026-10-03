from fastapi import FastAPI
from pydantic import BaseModel
import time
from app.feature_store import update_and_get_velocity
from app.model import model

app = FastAPI(title="Streaming Anomaly Detection Engine")

class TransactionEvent(BaseModel):
    user_id: str
    amount: float

@app.post("/predict")
async def predict_anomaly(event: TransactionEvent):
    start_time = time.perf_counter()
    
    velocity = await update_and_get_velocity(event.user_id)
    score = model.predict(event.amount, velocity)
    
    latency_ms = (time.perf_counter() - start_time) * 1000
    
    return {
        "user_id": event.user_id,
        "anomaly_score": score,
        "is_anomaly": score > 0.8,
        "latency_ms": round(latency_ms, 2)
    }