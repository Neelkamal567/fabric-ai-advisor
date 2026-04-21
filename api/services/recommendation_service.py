"""
Recommendation Service — Bridge between API and ML engine.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ml.recommend import get_recommender


class RecommendationService:
    """Service layer for fabric recommendations."""

    def __init__(self):
        self.recommender = get_recommender()

    def get_options(self):
        """Get valid input options."""
        return self.recommender.get_valid_options()

    def _get_fabric_details(self, fabric_type: str) -> dict:
        """Return hardcoded rich details for fabrics for the detailed view."""
        details = {
            "Cotton": {
                "image_url": "/static/assets/images/natural.png",
                "advantages": ["Highly breathable", "Soft on skin", "Easy to wash", "Affordable"],
                "disadvantages": ["Wrinkles easily", "Can shrink", "Absorbs moisture and stays wet"],
                "care_instructions": "Machine wash cold. Tumble dry low. Iron on medium to high heat."
            },
            "Silk": {
                "image_url": "/static/assets/images/premium.png",
                "advantages": ["Luxurious feel", "Beautiful drape", "Hypoallergenic", "Strong natural fiber"],
                "disadvantages": ["Expensive", "Requires special care", "Can watermark easily"],
                "care_instructions": "Dry clean recommended. Hand wash carefully in cold water. Do not wring."
            },
            "Denim": {
                "image_url": "/static/assets/images/heavy.png",
                "advantages": ["Extremely durable", "Hides stains", "Comfortable with wear", "Classic aesthetic"],
                "disadvantages": ["Heavy", "Slow to dry", "Can be stiff initially"],
                "care_instructions": "Wash inside out in cold water. Air dry to prevent shrinking and fading."
            },
            "Polyester": {
                "image_url": "/static/assets/images/synthetic.png",
                "advantages": ["Very durable", "Wrinkle-resistant", "Quick drying", "Affordable"],
                "disadvantages": ["Not very breathable", "Retains odors", "Environmental impact (microplastics)"],
                "care_instructions": "Machine wash warm. Tumble dry low. Do not iron at high heat."
            },
            "Linen": {
                "image_url": "/static/assets/images/natural.png",
                "advantages": ["Exceptional breathability", "Stronger when wet", "Eco-friendly", "Naturally cooling"],
                "disadvantages": ["Wrinkles very easily", "Can feel stiff initially", "Expensive"],
                "care_instructions": "Machine wash on gentle. Do not tumble dry completely (iron while damp)."
            },
            "Bamboo": {
                "image_url": "/static/assets/images/natural.png",
                "advantages": ["Ultra soft", "Antibacterial", "Highly sustainable", "Moisture wicking"],
                "disadvantages": ["Can pill", "Slower to dry than synthetics"],
                "care_instructions": "Machine wash gentle in cold water. Line dry."
            },
            "Wool": {
                "image_url": "/static/assets/images/heavy.png",
                "advantages": ["Excellent insulation", "Natural elasticity", "Odor resistant", "Flame retardant"],
                "disadvantages": ["Can be itchy", "Requires special washing", "Expensive"],
                "care_instructions": "Hand wash or use wool cycle in cold water. Dry flat, do not wring."
            },
            "Modal": {
                "image_url": "/static/assets/images/synthetic.png",
                "advantages": ["Very soft", "Resists shrinking", "Drapes well", "Breathable"],
                "disadvantages": ["Prone to stretching", "Not as durable as cotton"],
                "care_instructions": "Machine wash gentle. Tumble dry low. Iron on low."
            },
            "Velvet": {
                "image_url": "/static/assets/images/premium.png",
                "advantages": ["Luxurious texture", "Warm", "Rich appearance", "Soft"],
                "disadvantages": ["Hard to clean", "Attracts dust", "Expensive"],
                "care_instructions": "Dry clean only. Do not iron directly."
            }
        }
        
        # Fallback categories
        if fabric_type in details:
            return details[fabric_type]
            
        is_synthetic = fabric_type in ["Nylon", "Spandex", "Lycra", "Acrylic", "Chiffon", "Georgette", "Crepe", "Organza", "Satin"]
        is_premium = fabric_type in ["Cashmere", "Brocade"]
        is_heavy = fabric_type in ["Tweed", "Corduroy", "Jute"]
        
        if is_synthetic:
            return {
                "image_url": "/static/assets/images/synthetic.png",
                "advantages": ["Durable", "Affordable", "Wrinkle-resistant"],
                "disadvantages": ["Less breathable", "Synthetic feel"],
                "care_instructions": "Machine wash cold. Tumble dry low."
            }
        elif is_premium:
            return {
                "image_url": "/static/assets/images/premium.png",
                "advantages": ["Luxurious", "Premium feel", "Status symbol"],
                "disadvantages": ["Expensive", "Requires special care"],
                "care_instructions": "Dry clean only."
            }
        elif is_heavy:
            return {
                "image_url": "/static/assets/images/heavy.png",
                "advantages": ["Very durable", "Textured", "Warm"],
                "disadvantages": ["Heavy", "Stiff"],
                "care_instructions": "Dry clean or wash carefully."
            }
        else:
            return {
                "image_url": "/static/assets/images/natural.png",
                "advantages": ["Comfortable", "Versatile"],
                "disadvantages": ["Varies by blend"],
                "care_instructions": "Follow standard care procedures."
            }

    def _generate_fabric_reasoning(self, fabric: dict, weather: str, festival: str, purpose: str) -> str:
        """Generate specific 'Why this fabric' reasoning."""
        reasons = []
        name = fabric.get("fabric_type", "This fabric")
        
        if fabric.get("breathability", 0) >= 8 and weather in ["summer", "humid"]:
            reasons.append(f"its exceptional breathability ({fabric['breathability']}/10) makes it perfect for {weather} conditions")
        elif fabric.get("durability", 0) >= 8 and purpose in ["Sports", "Work/Labor", "Travel"]:
            reasons.append(f"its high durability ({fabric['durability']}/10) is ideal for {purpose}")
        elif fabric.get("comfort_level", 0) >= 8:
            reasons.append(f"it provides maximum comfort for {purpose}")
        else:
            reasons.append("it matches your usage profile well")
            
        if fabric.get("moisture_wicking") == "Yes":
            reasons.append("its moisture-wicking properties keep you dry")
            
        if fabric.get("sustainability_score", 0) >= 9:
            reasons.append("it is a highly sustainable, eco-friendly choice")
            
        if len(reasons) > 1:
            reason_str = ", ".join(reasons[:-1]) + ", and " + reasons[-1]
        else:
            reason_str = reasons[0]
            
        return f"{name} is recommended because {reason_str}."

    def get_recommendations(self, weather: str, festival: str, purpose: str, top_n: int = 5):
        """Get fabric recommendations and enrich them with details and reasoning."""
        results = self.recommender.recommend(weather, festival, purpose, top_n=top_n)
        
        # Enrich results with images, details, and reasoning
        for r in results:
            fabric_name = r.get("fabric_type", "")
            details = self._get_fabric_details(fabric_name)
            
            r["image_url"] = details["image_url"]
            r["advantages"] = details["advantages"]
            r["disadvantages"] = details["disadvantages"]
            r["care_instructions"] = details["care_instructions"]
            r["why_this_fabric"] = self._generate_fabric_reasoning(r, weather, festival, purpose)
            
        return results

    def generate_explanation(self, weather: str, festival: str, purpose: str, recommendations: list):
        """Generate a human-readable explanation for the recommendations."""
        if not recommendations:
            return "No suitable fabric recommendations found for the given criteria."

        top = recommendations[0]
        explanation_parts = [
            f"Based on your requirements ({weather} weather, {festival} occasion, {purpose} purpose), "
            f"I recommend **{top['fabric_type']}** as the best choice.\n\n"
        ]

        # Explain why
        reasons = []
        if top.get("breathability", 0) >= 7:
            reasons.append(f"excellent breathability ({top['breathability']}/10)")
        if top.get("comfort_level", 0) >= 7:
            reasons.append(f"high comfort ({top['comfort_level']}/10)")
        if top.get("durability", 0) >= 7:
            reasons.append(f"great durability ({top['durability']}/10)")
        if top.get("sustainability_score", 0) >= 7:
            reasons.append(f"eco-friendly (sustainability: {top['sustainability_score']}/10)")

        if reasons:
            explanation_parts.append(f"**Why {top['fabric_type']}?** It offers " + ", ".join(reasons) + ". ")

        explanation_parts.append(
            f"It falls in the **{top.get('cost_category', 'N/A')}** cost range "
            f"and is **{top.get('weight', 'N/A')}** weight fabric."
        )

        if len(recommendations) > 1:
            alternatives = [r["fabric_type"] for r in recommendations[1:3]]
            explanation_parts.append(
                f"\n\n**Alternatives:** {', '.join(alternatives)} are also great options for your needs."
            )

        return "".join(explanation_parts)

    @property
    def is_model_loaded(self):
        return self.recommender.artifacts is not None

    @property
    def is_dataset_loaded(self):
        return self.recommender.dataset is not None


# Singleton
_service = None


def get_recommendation_service():
    global _service
    if _service is None:
        _service = RecommendationService()
    return _service
