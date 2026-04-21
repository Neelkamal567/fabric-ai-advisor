"""
Recommendation Engine — Combines ML model with rule-based scoring
Provides fabric recommendations based on weather, festival, and purpose.
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np

# Fix Windows console encoding for Unicode output
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "fabric_recommender.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "unified_fabric_dataset.csv")


class FabricRecommender:
    """Hybrid recommendation engine using ML + rule-based scoring."""

    def __init__(self):
        self.artifacts = None
        self.dataset = None
        self._load()

    def _load(self):
        """Load trained model artifacts and dataset."""
        if os.path.exists(MODEL_PATH):
            self.artifacts = joblib.load(MODEL_PATH)
            print("✅ ML model loaded successfully")
        else:
            print("⚠️ ML model not found, using rule-based recommendations only")

        if os.path.exists(DATA_PATH):
            self.dataset = pd.read_csv(DATA_PATH)
            # Pandas reads the string "None" as NaN — restore it
            self.dataset["festival"] = self.dataset["festival"].fillna("None")
            print(f"✅ Dataset loaded: {len(self.dataset)} records")
        else:
            print("⚠️ Dataset not found")

    def get_valid_options(self):
        """Return valid input options for the frontend."""
        if self.artifacts:
            return {
                "weathers": self.artifacts["valid_weathers"],
                "festivals": self.artifacts["valid_festivals"],
                "purposes": self.artifacts["valid_purposes"],
            }
        elif self.dataset is not None:
            return {
                "weathers": sorted(self.dataset["weather"].unique().tolist()),
                "festivals": sorted(self.dataset["festival"].unique().tolist()),
                "purposes": sorted(self.dataset["purpose"].unique().tolist()),
            }
        return {"weathers": [], "festivals": [], "purposes": []}

    def _ml_predict(self, weather, festival, purpose, top_n=3):
        """Use ML model to predict top fabric recommendations."""
        if not self.artifacts:
            return []

        model = self.artifacts["model"]
        encoders = self.artifacts["encoders"]

        try:
            weather_enc = encoders["weather"].transform([weather])[0]
            festival_enc = encoders["festival"].transform([festival])[0]
            purpose_enc = encoders["purpose"].transform([purpose])[0]
        except ValueError:
            return []  # Unknown category — fall back to rule-based

        # We need to create feature vectors for prediction
        # Since the model also uses fabric properties as features,
        # we predict by scoring each possible fabric
        fabric_props = self.artifacts["fabric_properties"]
        predictions = []

        for fp in fabric_props:
            features = np.array([[
                weather_enc, festival_enc, purpose_enc,
                fp["comfort_level"], fp["durability"],
                fp["breathability"], fp["sustainability_score"]
            ]])

            fabric_name = fp["fabric_type"]
            try:
                fabric_enc = encoders["fabric_type"].transform([fabric_name])[0]
            except ValueError:
                continue

            # Get probability for this fabric being the right choice
            proba = model.predict_proba(features)[0]
            fabric_idx = list(model.classes_).index(fabric_enc) if fabric_enc in model.classes_ else -1

            if fabric_idx >= 0:
                predictions.append({
                    "fabric_type": fabric_name,
                    "ml_confidence": round(float(proba[fabric_idx]) * 100, 1),
                    **{k: v for k, v in fp.items() if k != "fabric_type"}
                })

        # Sort by ML confidence
        predictions.sort(key=lambda x: x["ml_confidence"], reverse=True)
        return predictions[:top_n]

    def _rule_based_recommend(self, weather, festival, purpose, top_n=3):
        """Use rule-based scoring from the dataset."""
        if self.dataset is None:
            return []

        df = self.dataset.copy()

        # Filter by exact match on inputs
        mask = pd.Series([True] * len(df))

        if weather and weather in df["weather"].values:
            mask &= df["weather"] == weather
        if festival and festival in df["festival"].values:
            mask &= df["festival"] == festival
        if purpose and purpose in df["purpose"].values:
            mask &= df["purpose"] == purpose

        filtered = df[mask]

        if filtered.empty:
            # Relax: try matching any 2 of 3
            mask_wf = (df["weather"] == weather) & (df["festival"] == festival)
            mask_wp = (df["weather"] == weather) & (df["purpose"] == purpose)
            mask_fp = (df["festival"] == festival) & (df["purpose"] == purpose)
            filtered = df[mask_wf | mask_wp | mask_fp]

        if filtered.empty:
            # Further relax: match any 1
            filtered = df[(df["weather"] == weather) | (df["festival"] == festival) | (df["purpose"] == purpose)]

        if filtered.empty:
            return []

        # Group by fabric, take the max suitability score
        grouped = (
            filtered.groupby("fabric_type")
            .agg({
                "suitability_score": "max",
                "comfort_level": "first",
                "durability": "first",
                "breathability": "first",
                "sustainability_score": "first",
                "cost_category": "first",
                "weight": "first",
                "moisture_wicking": "first",
                "match_strength": "max",
            })
            .reset_index()
        )

        # Sort by match strength then suitability score
        grouped = grouped.sort_values(
            ["match_strength", "suitability_score"], ascending=[False, False]
        )

        results = []
        for _, row in grouped.head(top_n).iterrows():
            results.append({
                "fabric_type": row["fabric_type"],
                "suitability_score": float(row["suitability_score"]),
                "comfort_level": int(row["comfort_level"]),
                "durability": int(row["durability"]),
                "breathability": int(row["breathability"]),
                "sustainability_score": int(row["sustainability_score"]),
                "cost_category": row["cost_category"],
                "weight": row["weight"],
                "moisture_wicking": row["moisture_wicking"],
                "match_strength": int(row["match_strength"]),
            })

        return results

    def recommend(self, weather, festival, purpose, top_n=5):
        """
        Get top-N fabric recommendations combining ML and rule-based approaches.

        Returns a list of dicts with fabric details and scores.
        """
        # Get ML predictions
        ml_results = self._ml_predict(weather, festival, purpose, top_n=top_n)

        # Get rule-based results
        rule_results = self._rule_based_recommend(weather, festival, purpose, top_n=top_n)

        # Merge: prioritize rule-based (more interpretable), enrich with ML confidence
        ml_lookup = {r["fabric_type"]: r.get("ml_confidence", 0) for r in ml_results}

        final_results = []
        seen = set()

        # First add rule-based results
        for r in rule_results:
            fabric = r["fabric_type"]
            if fabric not in seen:
                r["ml_confidence"] = ml_lookup.get(fabric, 0)
                # Compute combined score
                r["combined_score"] = round(
                    r["suitability_score"] * 0.7 + (r["ml_confidence"] / 100) * 10 * 0.3, 2
                )
                final_results.append(r)
                seen.add(fabric)

        # Then add ML-only results not in rule-based
        for r in ml_results:
            fabric = r["fabric_type"]
            if fabric not in seen:
                r["suitability_score"] = round(
                    (r["comfort_level"] + r["durability"] + r["breathability"] + r["sustainability_score"]) / 4, 2
                )
                r["combined_score"] = round(r["ml_confidence"] / 10, 2)
                r["match_strength"] = 1
                final_results.append(r)
                seen.add(fabric)

        # Sort by combined score
        final_results.sort(key=lambda x: x.get("combined_score", 0), reverse=True)

        return final_results[:top_n]


# Singleton instance
_recommender = None


def get_recommender():
    """Get or create the singleton recommender instance."""
    global _recommender
    if _recommender is None:
        _recommender = FabricRecommender()
    return _recommender


if __name__ == "__main__":
    recommender = get_recommender()
    print("\n" + "=" * 60)
    print("  Testing recommendations")
    print("=" * 60)

    test_cases = [
        ("summer", "Wedding", "Party"),
        ("winter", "Diwali", "Ethnic Wear"),
        ("rainy", "None", "Office"),
        ("humid", "Casual Outing", "Daily Wear"),
    ]

    for weather, festival, purpose in test_cases:
        print(f"\n🔍 Query: weather={weather}, festival={festival}, purpose={purpose}")
        results = recommender.recommend(weather, festival, purpose, top_n=3)
        for i, r in enumerate(results, 1):
            print(f"   {i}. {r['fabric_type']} (score: {r.get('combined_score', 'N/A')}, "
                  f"comfort: {r['comfort_level']}, durability: {r['durability']}, "
                  f"breathability: {r['breathability']}, cost: {r['cost_category']})")
