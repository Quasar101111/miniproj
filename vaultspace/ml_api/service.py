from fastapi import FastAPI
from pathlib import Path
import tensorflow as tf

app = FastAPI()

# Adjust the path based on your project structure
MODEL_PATH = Path(__file__).resolve().parent.parent / 'ml_models' / 'warehouse_recsys_v2'

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"Successfully loaded model from {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")
    raise

@app.post("/recommend")
async def get_recommendations(tenant_id: str, warehouse_ids: list[str]):
    try:
        # Generate predictions (simplified example)
        inputs = {
            "tenant_id": [tf.constant(tenant_id)]*len(warehouse_ids),
            "warehouse_id": tf.constant(warehouse_ids),
            "numerical_features": tf.constant([[0.5]*5]*len(warehouse_ids)),  # Replace with actual features
            "facilities": tf.constant([[1.0]*10]*len(warehouse_ids))  # Update facilities
        }
        
        predictions = model(inputs).numpy().flatten()
        ranked = [wid for _, wid in sorted(zip(predictions, warehouse_ids), reverse=True)]
        return {"recommendations": ranked[:5]}
    
    except Exception as e:
        return {"error": str(e)}