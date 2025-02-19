# import tensorflow as tf
# import logging
# import os
# from django.conf import settings
# import numpy as np

# logger = logging.getLogger(__name__)

# class RecommendationModel:
#     _instance = None
    
#     def __init__(self):
#         self.model = None
#         self.load_model()
        
#     @classmethod
#     def get_instance(cls):
#         if cls._instance is None:
#             cls._instance = cls()
#         return cls._instance
        
#     def load_model(self):
#         try:
#             # model_path = os.path.join(settings.BASE_DIR, 'ml_models\warehouse_recsys_v2.keras')
            
#             # Verify model file exists
#             if not os.path.isfile(model_path):
#                 raise FileNotFoundError(f"Model file not found at {model_path}")
            
#             # Check file size (minimum 1MB as sanity check)
#             if os.path.getsize(model_path) < 1024*1024:
#                 raise ValueError("Model file appears too small (corrupted?)")
            
#             # Load model with custom objects and safety checks
#             self.model = tf.keras.models.load_model(
#                 model_path,
#                 custom_objects=None,
#                 compile=False,
#                 safe_mode=True  # Enable Keras safe deserialization
#             )
#             logger.info(f"✅ Successfully loaded Keras model from {model_path}")
            
#             # Verify model structure
#             required_inputs = ['tenant_id', 'warehouse_id', 'numerical_features', 'facilities']
#             for inp in required_inputs:
#                 if inp not in self.model.input_names:
#                     raise ValueError(f"Model missing expected input: {inp}")
            
#             # Test prediction with proper input format
#             test_input = {
#                 "tenant_id": np.array([0], dtype=np.int32),
#                 "warehouse_id": np.array([0], dtype=np.int32),
#                 "numerical_features": np.array([[0.0]*5], dtype=np.float32),
#                 "facilities": np.array([[0.0]*10], dtype=np.float32)
#             }
            
#             try:
#                 test_pred = self.model.predict(test_input)
#                 logger.info(f"✅ Model test prediction succeeded. Output shape: {test_pred.shape}")
#             except Exception as e:
#                 raise RuntimeError(f"Model test prediction failed: {str(e)}")
            
#             return True

#         except Exception as e:
#             logger.error(f"❌ Keras model loading failed: {str(e)}")
#             self.model = None
#             raise RuntimeError(f"Model load error: {str(e)}") from e

# # Initialize during app startup
# model_loader = RecommendationModel.get_instance()