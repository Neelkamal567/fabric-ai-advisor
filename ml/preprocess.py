"""
Data Preprocessing & Merging Script
Cleans all raw datasets and creates a unified fabric recommendation dataset.
"""

import pandas as pd
import numpy as np
import os
import sys

# Fix Windows console encoding for Unicode output
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


def load_raw_data():
    """Load all raw CSV files."""
    fabric_df = pd.read_csv(os.path.join(RAW_DIR, "fabric_properties.csv"))
    weather_df = pd.read_csv(os.path.join(RAW_DIR, "weather_categories.csv"))
    festival_df = pd.read_csv(os.path.join(RAW_DIR, "festival_mapping.csv"))
    purpose_df = pd.read_csv(os.path.join(RAW_DIR, "purpose_mapping.csv"))

    print(f"📦 Loaded fabric_properties: {fabric_df.shape}")
    print(f"📦 Loaded weather_categories: {weather_df.shape}")
    print(f"📦 Loaded festival_mapping: {festival_df.shape}")
    print(f"📦 Loaded purpose_mapping: {purpose_df.shape}")

    return fabric_df, weather_df, festival_df, purpose_df


def normalize_columns(df):
    """Normalize column names to lowercase with underscores."""
    df.columns = [col.strip().lower().replace(" ", "_").replace("-", "_") for col in df.columns]
    return df


def clean_data(fabric_df, weather_df, festival_df, purpose_df):
    """Clean and normalize all datasets."""
    # Normalize column names
    fabric_df = normalize_columns(fabric_df)
    weather_df = normalize_columns(weather_df)
    festival_df = normalize_columns(festival_df)
    purpose_df = normalize_columns(purpose_df)

    # Strip whitespace from string columns
    for df in [fabric_df, weather_df, festival_df, purpose_df]:
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].str.strip()

    # Handle missing values in fabric properties
    numeric_cols = ["comfort_level", "durability", "breathability", "sustainability_score"]
    for col in numeric_cols:
        if col in fabric_df.columns:
            fabric_df[col] = fabric_df[col].fillna(fabric_df[col].median())

    fabric_df["cost_category"] = fabric_df["cost_category"].fillna("Medium")
    fabric_df["moisture_wicking"] = fabric_df["moisture_wicking"].fillna("No")

    # Remove duplicates
    fabric_df = fabric_df.drop_duplicates(subset=["fabric_type"])
    weather_df = weather_df.drop_duplicates(subset=["weather"])
    festival_df = festival_df.drop_duplicates(subset=["festival"])
    purpose_df = purpose_df.drop_duplicates(subset=["purpose"])

    print("🧹 Data cleaning completed")
    return fabric_df, weather_df, festival_df, purpose_df


def compute_suitability_score(row, context_weights):
    """
    Compute fabric suitability score based on context-specific weights.

    score = (comfort × w1) + (durability × w2) + (breathability × w3) + (sustainability × w4)
    """
    w = context_weights
    score = (
        row["comfort_level"] * w.get("comfort", 0.25)
        + row["durability"] * w.get("durability", 0.25)
        + row["breathability"] * w.get("breathability", 0.25)
        + row["sustainability_score"] * w.get("sustainability", 0.25)
    )
    return round(score, 2)


def get_context_weights(weather, purpose):
    """Get scoring weights based on weather and purpose context."""
    # Default balanced weights
    weights = {"comfort": 0.25, "durability": 0.25, "breathability": 0.25, "sustainability": 0.25}

    # Weather-specific adjustments
    weather_weights = {
        "summer": {"comfort": 0.2, "durability": 0.15, "breathability": 0.45, "sustainability": 0.2},
        "winter": {"comfort": 0.35, "durability": 0.30, "breathability": 0.10, "sustainability": 0.25},
        "rainy": {"comfort": 0.15, "durability": 0.40, "breathability": 0.15, "sustainability": 0.30},
        "humid": {"comfort": 0.20, "durability": 0.15, "breathability": 0.45, "sustainability": 0.20},
        "autumn": {"comfort": 0.30, "durability": 0.25, "breathability": 0.20, "sustainability": 0.25},
    }

    # Purpose-specific adjustments
    purpose_weights = {
        "Sports": {"comfort": 0.20, "durability": 0.40, "breathability": 0.30, "sustainability": 0.10},
        "Office": {"comfort": 0.35, "durability": 0.25, "breathability": 0.25, "sustainability": 0.15},
        "Party": {"comfort": 0.30, "durability": 0.15, "breathability": 0.20, "sustainability": 0.35},
        "Outdoor": {"comfort": 0.15, "durability": 0.45, "breathability": 0.25, "sustainability": 0.15},
        "Work/Labor": {"comfort": 0.15, "durability": 0.50, "breathability": 0.20, "sustainability": 0.15},
        "Travel": {"comfort": 0.30, "durability": 0.30, "breathability": 0.25, "sustainability": 0.15},
        "Loungewear": {"comfort": 0.50, "durability": 0.15, "breathability": 0.20, "sustainability": 0.15},
        "Daily Wear": {"comfort": 0.30, "durability": 0.25, "breathability": 0.25, "sustainability": 0.20},
    }

    # Blend weather and purpose weights
    w_weights = weather_weights.get(weather, weights)
    p_weights = purpose_weights.get(purpose, weights)

    blended = {}
    for key in weights:
        blended[key] = round((w_weights.get(key, 0.25) + p_weights.get(key, 0.25)) / 2, 3)

    return blended


def merge_datasets(fabric_df, weather_df, festival_df, purpose_df):
    """
    Create unified dataset by cross-matching fabrics with weather, festival, and purpose.
    Only creates valid combinations where the fabric is recommended.
    """
    records = []

    for _, weather_row in weather_df.iterrows():
        weather = weather_row["weather"]
        rec_fabrics_weather = set(f.strip() for f in weather_row["recommended_fabrics"].split(","))

        for _, festival_row in festival_df.iterrows():
            festival = festival_row["festival"]
            rec_fabrics_festival = set(f.strip() for f in festival_row["recommended_fabrics"].split(","))

            for _, purpose_row in purpose_df.iterrows():
                purpose = purpose_row["purpose"]
                rec_fabrics_purpose = set(f.strip() for f in purpose_row["recommended_fabrics"].split(","))

                # Find fabrics that appear in at least 2 of the 3 recommendation lists
                all_fabrics = rec_fabrics_weather | rec_fabrics_festival | rec_fabrics_purpose

                for fabric_name in all_fabrics:
                    match_count = sum([
                        fabric_name in rec_fabrics_weather,
                        fabric_name in rec_fabrics_festival,
                        fabric_name in rec_fabrics_purpose,
                    ])

                    # Include if fabric matches at least 2 contexts
                    if match_count >= 2:
                        fabric_info = fabric_df[fabric_df["fabric_type"] == fabric_name]
                        if fabric_info.empty:
                            continue

                        fi = fabric_info.iloc[0]
                        context_weights = get_context_weights(weather, purpose)
                        suitability = compute_suitability_score(fi, context_weights)

                        # Bonus for matching all 3 contexts
                        if match_count == 3:
                            suitability = round(suitability * 1.15, 2)
                            suitability = min(suitability, 10.0)

                        records.append({
                            "fabric_type": fabric_name,
                            "weather": weather,
                            "festival": festival,
                            "purpose": purpose,
                            "comfort_level": fi["comfort_level"],
                            "durability": fi["durability"],
                            "breathability": fi["breathability"],
                            "sustainability_score": fi["sustainability_score"],
                            "cost_category": fi["cost_category"],
                            "weight": fi["weight"],
                            "moisture_wicking": fi["moisture_wicking"],
                            "suitability_score": suitability,
                            "match_strength": match_count,
                        })

    unified_df = pd.DataFrame(records)

    # Remove exact duplicates
    unified_df = unified_df.drop_duplicates()

    # Sort by suitability score descending
    unified_df = unified_df.sort_values("suitability_score", ascending=False).reset_index(drop=True)

    return unified_df


def main():
    print("=" * 60)
    print("  AI Fabric Advisor — Data Preprocessing & Merging")
    print("=" * 60)
    print()

    # Load data
    fabric_df, weather_df, festival_df, purpose_df = load_raw_data()
    print()

    # Clean data
    fabric_df, weather_df, festival_df, purpose_df = clean_data(
        fabric_df, weather_df, festival_df, purpose_df
    )
    print()

    # Merge datasets
    print("🔗 Merging datasets...")
    unified_df = merge_datasets(fabric_df, weather_df, festival_df, purpose_df)
    print(f"   Generated {len(unified_df)} recommendation records")
    print()

    # Summary statistics
    print("📊 Dataset Summary:")
    print(f"   Unique fabrics: {unified_df['fabric_type'].nunique()}")
    print(f"   Weather categories: {unified_df['weather'].nunique()}")
    print(f"   Festivals/Occasions: {unified_df['festival'].nunique()}")
    print(f"   Purposes: {unified_df['purpose'].nunique()}")
    print(f"   Suitability score range: {unified_df['suitability_score'].min()} - {unified_df['suitability_score'].max()}")
    print(f"   Average suitability score: {unified_df['suitability_score'].mean():.2f}")
    print()

    # Export
    output_path = os.path.join(PROCESSED_DIR, "unified_fabric_dataset.csv")
    unified_df.to_csv(output_path, index=False)
    print(f"✅ Exported unified dataset to: {os.path.abspath(output_path)}")
    print(f"   Total records: {len(unified_df)}")
    print()

    # Print top 10 records as sample
    print("📋 Top 10 records (highest suitability):")
    print(unified_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
