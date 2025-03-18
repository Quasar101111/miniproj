# app/recommender.py
import tensorflow as tf
import numpy as np
from typing import List, Tuple
from .schemas import WarehouseBase, TenantBase

class WarehouseRecommender:
    def __init__(self):
        self.model = self._build_model()
        
        # Initialize the model with random weights since no training is shown
        # This ensures the model can be used immediately
        self._initialize_model()
       
    def _build_model(self):
        # Input layers
        warehouse_input = tf.keras.layers.Input(shape=(8,))
        tenant_input = tf.keras.layers.Input(shape=(4,))
       
        # Warehouse processing
        w = tf.keras.layers.Dense(128, activation='relu')(warehouse_input)
        w = tf.keras.layers.BatchNormalization()(w)
        w = tf.keras.layers.Dropout(0.3)(w)
        w = tf.keras.layers.Dense(64, activation='relu')(w)
       
        # Tenant processing
        t = tf.keras.layers.Dense(64, activation='relu')(tenant_input)
        t = tf.keras.layers.BatchNormalization()(t)
        t = tf.keras.layers.Dropout(0.3)(t)
        t = tf.keras.layers.Dense(32, activation='relu')(t)
       
        # Combine
        combined = tf.keras.layers.Concatenate()([w, t])
       
        # Output
        x = tf.keras.layers.Dense(64, activation='relu')(combined)
        x = tf.keras.layers.Dropout(0.3)(x)
        output = tf.keras.layers.Dense(1, activation='sigmoid')(x)
       
        model = tf.keras.Model(
            inputs=[warehouse_input, tenant_input],
            outputs=output
        )
       
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
       
        return model
    
    def _initialize_model(self):
        """Initialize the model with some dummy data to ensure weights are set"""
        dummy_warehouse = np.random.random((1, 8))
        dummy_tenant = np.random.random((1, 4))
        self.model.predict([dummy_warehouse, dummy_tenant])
        
    def prepare_features(self, warehouse: WarehouseBase, tenant: TenantBase) -> Tuple[np.ndarray, np.ndarray]:
        # Warehouse features
        # Handle year_built as datetime object
        current_year = 2024
        try:
            year_built = warehouse.year_built.year
        except AttributeError:
            # Handle if it's a string or other format
            if isinstance(warehouse.year_built, str):
                year_built = int(warehouse.year_built.split('-')[0])
            else:
                year_built = 2000  # Default fallback
        
        w_features = np.array([
            warehouse.length / 1000,
            warehouse.width / 1000,
            warehouse.height / 100,
            warehouse.latitude / 90,
            warehouse.longitude / 180,
            warehouse.rental_price / 100000,
            len(warehouse.facilities) / 10,
            (current_year - year_built) / 100
        ])
       
        # Tenant features - with safer handling of optional fields
        avg_price = 50000  # Default
        if tenant.preferred_price_range:
            avg_price = sum(tenant.preferred_price_range) / 2
            
        tenant_lat = tenant.latitude if tenant.latitude is not None else 0
        tenant_lon = tenant.longitude if tenant.longitude is not None else 0
        
        t_features = np.array([
            tenant_lat / 90,
            tenant_lon / 180,
            avg_price / 100000,
            tenant.lease_history_count / 10
        ])
       
        return w_features, t_features
    
    def predict(self, warehouses: List[WarehouseBase], tenant: TenantBase) -> np.ndarray:
        if not warehouses:
            return np.array([])
            
        warehouse_features = []
        tenant_features = []
       
        for warehouse in warehouses:
            w_feat, t_feat = self.prepare_features(warehouse, tenant)
            warehouse_features.append(w_feat)
            tenant_features.append(t_feat)
       
        # Handle the case of multiple warehouses correctly
        return self.model.predict(
            [np.array(warehouse_features), np.array(tenant_features)],
            verbose=0  # Suppress prediction outputs
        ).flatten()