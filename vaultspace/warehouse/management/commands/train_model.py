from django.core.management import BaseCommand
import tensorflow as tf
import tensorflow_recommenders as tfrs
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
import os

# Suppress TensorFlow info messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Load and preprocess data
        df = pd.read_csv("media/exports/tenant_warehouse_data.csv")
        
        # Convert facilities to list of features
        df['facilities'] = df['facilities'].apply(lambda x: x.split(','))
        
        # Create facilities multi-hot encoding
        mlb = MultiLabelBinarizer()
        facilities_encoded = mlb.fit_transform(df['facilities'])
        num_facilities = facilities_encoded.shape[1]
        
        # Normalize numerical features
        scaler = StandardScaler()
        num_features = ['area', 'length', 'breadth', 'height', 'rental_price']
        df[num_features] = scaler.fit_transform(df[num_features])
        
        # Split data properly
        train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
        
        # Create TensorFlow datasets
        def df_to_dataset(dataframe, shuffle=True, batch_size=32):
            return tf.data.Dataset.from_tensor_slices((
                {
                    "tenant_id": tf.strings.as_string(dataframe.tenant_id.values),
                    "warehouse_id": tf.strings.as_string(dataframe.warehouse_id.values),
                    "numerical_features": tf.cast(dataframe[num_features].values, tf.float32),
                    "facilities": tf.cast(facilities_encoded[dataframe.index], tf.float32)
                },
                tf.cast(dataframe.rating.values, tf.float32)
            )).shuffle(1000).batch(batch_size).prefetch(tf.data.AUTOTUNE)

        train_dataset = df_to_dataset(train_df)
        test_dataset = df_to_dataset(test_df, shuffle=False)

        # Define the model with improved architecture
        class RecommendationModel(tfrs.Model):
            def __init__(self, unique_tenants, unique_warehouses, num_facilities):
                super().__init__()
                
                # Tenant Tower
                self.tenant_embedding = tf.keras.Sequential([
                    tf.keras.layers.StringLookup(vocabulary=unique_tenants),
                    tf.keras.layers.Embedding(len(unique_tenants) + 1, 64),
                    tf.keras.layers.Dropout(0.2)
                ])
                
                # Warehouse Tower
                self.warehouse_embedding = tf.keras.Sequential([
                    tf.keras.layers.StringLookup(vocabulary=unique_warehouses),
                    tf.keras.layers.Embedding(len(unique_warehouses) + 1, 64),
                    tf.keras.layers.Dropout(0.2)
                ])
                
                # Feature Processing
                self.numerical_dense = tf.keras.Sequential([
                    tf.keras.layers.Dense(128, activation='relu'),
                    tf.keras.layers.Dropout(0.3)
                ])
                
                self.facilities_dense = tf.keras.Sequential([
                    tf.keras.layers.Dense(64, activation='relu'),
                    tf.keras.layers.Dropout(0.2)
                ])
                
                # Final Prediction Layer
                self.rating_model = tf.keras.Sequential([
                    tf.keras.layers.Dense(256, activation='relu'),
                    tf.keras.layers.Dropout(0.4),
                    tf.keras.layers.Dense(128, activation='relu'),
                    tf.keras.layers.Dropout(0.3),
                    tf.keras.layers.Dense(1)
                ])
                
                self.task = tfrs.tasks.Ranking(
                    loss=tf.keras.losses.MeanSquaredError(),
                    metrics=[
                        tf.keras.metrics.RootMeanSquaredError(),
                        tf.keras.metrics.MeanAbsoluteError()
                    ]
                )

            def call(self, features):
                # Embeddings
                tenant_emb = self.tenant_embedding(features["tenant_id"])
                warehouse_emb = self.warehouse_embedding(features["warehouse_id"])
                
                # Process numerical features
                numerical = self.numerical_dense(features["numerical_features"])
                
                # Process facilities
                facilities = self.facilities_dense(features["facilities"])
                
                # Concatenate all features
                combined = tf.concat([
                    tenant_emb, 
                    warehouse_emb, 
                    numerical, 
                    facilities
                ], axis=1)
                
                return self.rating_model(combined)

            def compute_loss(self, inputs, training=False):
                features, labels = inputs  # Unpack tuple
                predictions = self(features)
                return self.task(labels=labels, predictions=predictions)

        # Get unique values
        unique_tenants = df.tenant_id.unique().astype(str)
        unique_warehouses = df.warehouse_id.unique().astype(str)
        
        # Initialize and train model
        model = RecommendationModel(unique_tenants, unique_warehouses, num_facilities)
        model.compile(optimizer=tf.keras.optimizers.Adam(0.001))
        
        # Add early stopping
        early_stopping = tf.keras.callbacks.EarlyStopping(
            patience=3,
            restore_best_weights=True,
            monitor='val_root_mean_squared_error',
            mode='min'
        )
        
        # Train with validation
        history = model.fit(
            train_dataset,
            epochs=20,
            validation_data=test_dataset,
            callbacks=[early_stopping]
        )
        
        # Evaluate final model
        test_results = model.evaluate(test_dataset, return_dict=True)
        self.stdout.write(f"Test RMSE: {test_results['root_mean_squared_error']:.4f}")
        self.stdout.write(f"Test MAE: {test_results['mean_absolute_error']:.4f}")

        # Save model
        model_dir = "ml_models"
        os.makedirs(model_dir, exist_ok=True)  # Create directory if not exists
        model.save(os.path.join(model_dir, "warehouse_recsys_v2.keras"))
        self.stdout.write(self.style.SUCCESS('Model training completed!'))
