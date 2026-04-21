"""
Model Training Script — Random Forest + Rule-Based Scoring
Trains a fabric recommendation model and saves it for inference.
"""

import pandas as pd
import numpy as np
import os
import sys
import joblib

# Fix Windows console encoding for Unicode output
sys.stdout.reconfigure(encoding='utf-8')
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "unified_fabric_dataset.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def load_data():
    """Load the unified dataset."""
    df = pd.read_csv(DATA_PATH)
    # Pandas reads the string "None" as NaN — restore it
    df["festival"] = df["festival"].fillna("None")
    print(f"📦 Loaded unified dataset: {df.shape}")
    return df


def prepare_features(df):
    """Prepare features for model training using label encoding."""
    encoders = {}

    # Encode categorical input features
    for col in ["weather", "festival", "purpose"]:
        le = LabelEncoder()
        df[f"{col}_encoded"] = le.fit_transform(df[col])
        encoders[col] = le

    # Encode target variable
    le_target = LabelEncoder()
    df["fabric_encoded"] = le_target.fit_transform(df["fabric_type"])
    encoders["fabric_type"] = le_target

    # Feature columns
    feature_cols = ["weather_encoded", "festival_encoded", "purpose_encoded"]

    # Also include numerical properties as features
    num_cols = ["comfort_level", "durability", "breathability", "sustainability_score"]
    feature_cols.extend(num_cols)

    X = df[feature_cols].values
    y = df["fabric_encoded"].values

    return X, y, encoders, feature_cols


def train_model(X, y, encoders):
    """Train Random Forest model."""
    print("\n🏋️ Training Random Forest Classifier...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    fabric_names = encoders["fabric_type"].classes_
    print(f"\n📊 Model Accuracy: {accuracy:.4f}")
    print("\n📋 Classification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=fabric_names,
        zero_division=0
    ))

    return model, accuracy


def save_artifacts(model, encoders, feature_cols, df):
    """Save model and encoders for inference."""
    artifacts = {
        "model": model,
        "encoders": encoders,
        "feature_cols": feature_cols,
        "fabric_properties": df[["fabric_type", "comfort_level", "durability",
                                  "breathability", "sustainability_score",
                                  "cost_category", "weight", "moisture_wicking"]].drop_duplicates().to_dict("records"),
        "valid_weathers": sorted(df["weather"].unique().tolist()),
        "valid_festivals": sorted(df["festival"].unique().tolist()),
        "valid_purposes": sorted(df["purpose"].unique().tolist()),
    }

    model_path = os.path.join(MODEL_DIR, "fabric_recommender.pkl")
    joblib.dump(artifacts, model_path)
    print(f"\n✅ Model saved to: {os.path.abspath(model_path)}")

    return model_path


def main():
    print("=" * 60)
    print("  AI Fabric Advisor — Model Training")
    print("=" * 60)
    print()

    # Load data
    df = load_data()

    # Prepare features
    X, y, encoders, feature_cols = prepare_features(df)
    print(f"   Features shape: {X.shape}")
    print(f"   Unique fabrics (classes): {len(encoders['fabric_type'].classes_)}")

    # Train model
    model, accuracy = train_model(X, y, encoders)

    # Save
    save_artifacts(model, encoders, feature_cols, df)

    print()
    print("=" * 60)
    print(f"  Training complete! Accuracy: {accuracy:.2%}")
    print("=" * 60)


if __name__ == "__main__":
    main()
