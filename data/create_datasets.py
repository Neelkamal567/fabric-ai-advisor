"""
Dataset Creation Script for AI Fabric & Material Advisor
Generates 4 synthetic CSV datasets based on domain knowledge from:
- Kaggle Fabric Classification Dataset
- Weather datasets (IMD / Kaggle)
- Flipkart E-commerce product categories
- Manual festival/occasion mapping
"""

import pandas as pd
import os
import sys
import random

# Fix Windows console encoding for Unicode output
sys.stdout.reconfigure(encoding='utf-8')

# Ensure output directories exist
RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(RAW_DIR, exist_ok=True)


def create_fabric_properties():
    """
    Create fabric_properties.csv with 25 fabric types and their attributes.
    Sourced from textile domain knowledge and Kaggle fabric classification datasets.
    """
    fabrics = [
        # (fabric_type, category, comfort, durability, breathability, sustainability, cost, weather_suit, weight, moisture_wicking)
        ("Cotton", "Natural", 9, 7, 9, 8, "Low", "summer,humid,all-season", "Light", "Yes"),
        ("Silk", "Natural", 8, 5, 6, 7, "Premium", "winter,all-season", "Light", "No"),
        ("Wool", "Natural", 7, 8, 4, 7, "High", "winter,autumn", "Heavy", "Yes"),
        ("Polyester", "Synthetic", 5, 9, 4, 3, "Low", "all-season,rainy", "Medium", "Yes"),
        ("Linen", "Natural", 8, 6, 10, 9, "Medium", "summer,humid", "Light", "No"),
        ("Nylon", "Synthetic", 5, 9, 3, 3, "Low", "rainy,all-season", "Light", "Yes"),
        ("Velvet", "Natural", 7, 6, 3, 5, "High", "winter,autumn", "Heavy", "No"),
        ("Khadi", "Natural", 8, 7, 8, 10, "Medium", "summer,all-season", "Medium", "Yes"),
        ("Denim", "Natural", 6, 9, 5, 6, "Medium", "winter,autumn,all-season", "Heavy", "No"),
        ("Chiffon", "Synthetic", 6, 4, 7, 4, "Medium", "summer,humid", "Light", "No"),
        ("Satin", "Synthetic", 7, 5, 5, 4, "High", "all-season", "Light", "No"),
        ("Rayon", "Semi-Synthetic", 7, 5, 7, 5, "Low", "summer,humid", "Light", "No"),
        ("Georgette", "Synthetic", 6, 4, 7, 4, "Medium", "summer,humid", "Light", "No"),
        ("Organza", "Synthetic", 4, 4, 6, 4, "High", "all-season", "Light", "No"),
        ("Crepe", "Synthetic", 6, 5, 6, 4, "Medium", "summer,all-season", "Light", "No"),
        ("Muslin", "Natural", 9, 5, 10, 9, "Low", "summer,humid", "Light", "No"),
        ("Bamboo", "Natural", 9, 6, 9, 10, "Medium", "summer,humid,all-season", "Light", "Yes"),
        ("Hemp", "Natural", 6, 9, 8, 10, "Medium", "summer,all-season", "Medium", "No"),
        ("Lycra", "Synthetic", 8, 7, 5, 3, "Medium", "all-season", "Light", "Yes"),
        ("Fleece", "Synthetic", 9, 7, 3, 3, "Low", "winter,autumn", "Medium", "Yes"),
        ("Corduroy", "Natural", 7, 8, 4, 6, "Medium", "winter,autumn", "Heavy", "No"),
        ("Tweed", "Natural", 6, 9, 3, 7, "High", "winter,autumn", "Heavy", "No"),
        ("Cashmere", "Natural", 10, 5, 5, 6, "Premium", "winter", "Medium", "No"),
        ("Jute", "Natural", 4, 8, 7, 10, "Low", "summer,all-season", "Heavy", "No"),
        ("Modal", "Semi-Synthetic", 8, 6, 8, 7, "Medium", "summer,all-season", "Light", "Yes"),
        ("Tencel", "Semi-Synthetic", 9, 7, 9, 9, "Medium", "summer,humid,all-season", "Light", "Yes"),
        ("Acrylic", "Synthetic", 6, 7, 3, 2, "Low", "winter,autumn", "Medium", "No"),
        ("Spandex", "Synthetic", 8, 6, 4, 2, "Medium", "all-season", "Light", "Yes"),
        ("Taffeta", "Synthetic", 5, 6, 4, 3, "Medium", "all-season,winter", "Medium", "No"),
        ("Brocade", "Natural", 5, 6, 3, 5, "Premium", "winter,all-season", "Heavy", "No"),
    ]

    df = pd.DataFrame(fabrics, columns=[
        "fabric_type", "category", "comfort_level", "durability",
        "breathability", "sustainability_score", "cost_category",
        "weather_suitability", "weight", "moisture_wicking"
    ])

    path = os.path.join(RAW_DIR, "fabric_properties.csv")
    df.to_csv(path, index=False)
    print(f"✅ Created fabric_properties.csv ({len(df)} fabrics)")
    return df


def create_weather_categories():
    """
    Create weather_categories.csv mapping weather conditions to fabric recommendations.
    Based on IMD weather data categories and textile suitability knowledge.
    """
    weather_data = [
        {
            "weather": "summer",
            "temp_range": "30-45°C",
            "humidity_range": "20-50%",
            "description": "Hot and dry summer conditions",
            "recommended_fabrics": "Cotton,Linen,Muslin,Khadi,Bamboo,Rayon,Chiffon,Georgette,Modal,Tencel",
            "avoid_fabrics": "Wool,Velvet,Fleece,Tweed,Corduroy,Cashmere,Acrylic",
            "priority_properties": "breathability,comfort"
        },
        {
            "weather": "winter",
            "temp_range": "0-15°C",
            "humidity_range": "30-60%",
            "description": "Cold winter conditions",
            "recommended_fabrics": "Wool,Velvet,Fleece,Tweed,Cashmere,Corduroy,Denim,Acrylic,Silk,Brocade",
            "avoid_fabrics": "Chiffon,Muslin,Linen,Georgette",
            "priority_properties": "warmth,durability"
        },
        {
            "weather": "rainy",
            "temp_range": "20-30°C",
            "humidity_range": "70-95%",
            "description": "Monsoon and rainy season conditions",
            "recommended_fabrics": "Polyester,Nylon,Lycra,Spandex,Denim",
            "avoid_fabrics": "Silk,Velvet,Cashmere,Wool,Jute,Brocade",
            "priority_properties": "durability,moisture_wicking"
        },
        {
            "weather": "humid",
            "temp_range": "25-35°C",
            "humidity_range": "60-85%",
            "description": "Hot and humid tropical conditions",
            "recommended_fabrics": "Cotton,Linen,Bamboo,Modal,Tencel,Muslin,Rayon,Chiffon,Georgette",
            "avoid_fabrics": "Wool,Velvet,Fleece,Acrylic,Tweed,Corduroy",
            "priority_properties": "breathability,moisture_wicking"
        },
        {
            "weather": "autumn",
            "temp_range": "15-25°C",
            "humidity_range": "40-65%",
            "description": "Mild autumn/spring transitional weather",
            "recommended_fabrics": "Cotton,Denim,Corduroy,Tweed,Khadi,Fleece,Velvet,Wool,Acrylic",
            "avoid_fabrics": "Chiffon,Organza",
            "priority_properties": "comfort,durability"
        },
    ]

    df = pd.DataFrame(weather_data)
    path = os.path.join(RAW_DIR, "weather_categories.csv")
    df.to_csv(path, index=False)
    print(f"✅ Created weather_categories.csv ({len(df)} categories)")
    return df


def create_festival_mapping():
    """
    Create festival_mapping.csv with occasion-to-fabric cultural mappings.
    Manually curated based on Indian and global cultural traditions.
    """
    festivals = [
        {
            "festival": "Wedding",
            "recommended_fabrics": "Silk,Velvet,Brocade,Satin,Organza,Georgette,Cashmere",
            "formality_level": "Ultra-formal",
            "cultural_context": "Universal",
            "description": "Grand wedding ceremonies and receptions"
        },
        {
            "festival": "Diwali",
            "recommended_fabrics": "Silk,Khadi,Brocade,Satin,Velvet,Georgette",
            "formality_level": "Formal",
            "cultural_context": "Indian",
            "description": "Festival of lights celebration"
        },
        {
            "festival": "Eid",
            "recommended_fabrics": "Silk,Chiffon,Georgette,Cotton,Satin,Crepe",
            "formality_level": "Formal",
            "cultural_context": "Indian",
            "description": "Islamic festival celebration"
        },
        {
            "festival": "Christmas",
            "recommended_fabrics": "Velvet,Silk,Satin,Wool,Cashmere,Brocade",
            "formality_level": "Semi-formal",
            "cultural_context": "Western",
            "description": "Christmas celebration and parties"
        },
        {
            "festival": "Holi",
            "recommended_fabrics": "Cotton,Polyester,Khadi,Denim",
            "formality_level": "Casual",
            "cultural_context": "Indian",
            "description": "Festival of colors - needs washable fabrics"
        },
        {
            "festival": "Pongal",
            "recommended_fabrics": "Silk,Cotton,Khadi",
            "formality_level": "Formal",
            "cultural_context": "Indian",
            "description": "South Indian harvest festival"
        },
        {
            "festival": "Onam",
            "recommended_fabrics": "Cotton,Silk,Khadi,Muslin",
            "formality_level": "Formal",
            "cultural_context": "Indian",
            "description": "Kerala harvest festival"
        },
        {
            "festival": "Durga Puja",
            "recommended_fabrics": "Silk,Georgette,Chiffon,Satin,Cotton",
            "formality_level": "Formal",
            "cultural_context": "Indian",
            "description": "Bengali festival celebration"
        },
        {
            "festival": "Navratri",
            "recommended_fabrics": "Cotton,Silk,Georgette,Chiffon,Crepe",
            "formality_level": "Semi-formal",
            "cultural_context": "Indian",
            "description": "Nine nights of dance and celebration"
        },
        {
            "festival": "New Year",
            "recommended_fabrics": "Silk,Satin,Velvet,Georgette,Crepe,Lycra",
            "formality_level": "Semi-formal",
            "cultural_context": "Universal",
            "description": "New Year's Eve party celebrations"
        },
        {
            "festival": "Casual Outing",
            "recommended_fabrics": "Cotton,Denim,Linen,Khadi,Modal,Bamboo,Rayon",
            "formality_level": "Casual",
            "cultural_context": "Universal",
            "description": "Everyday casual outings and hangouts"
        },
        {
            "festival": "Office Event",
            "recommended_fabrics": "Cotton,Linen,Polyester,Crepe,Modal",
            "formality_level": "Semi-formal",
            "cultural_context": "Universal",
            "description": "Corporate events and office gatherings"
        },
        {
            "festival": "Interview",
            "recommended_fabrics": "Cotton,Linen,Polyester,Crepe",
            "formality_level": "Formal",
            "cultural_context": "Universal",
            "description": "Job interviews and professional meetings"
        },
        {
            "festival": "Graduation",
            "recommended_fabrics": "Cotton,Silk,Polyester,Crepe,Satin",
            "formality_level": "Semi-formal",
            "cultural_context": "Universal",
            "description": "Graduation ceremonies and convocations"
        },
        {
            "festival": "Date Night",
            "recommended_fabrics": "Silk,Satin,Velvet,Chiffon,Crepe,Georgette,Lycra",
            "formality_level": "Semi-formal",
            "cultural_context": "Universal",
            "description": "Romantic dinner or evening out"
        },
        {
            "festival": "None",
            "recommended_fabrics": "Cotton,Polyester,Denim,Linen,Modal,Bamboo,Khadi",
            "formality_level": "Casual",
            "cultural_context": "Universal",
            "description": "No special occasion - everyday wear"
        },
    ]

    df = pd.DataFrame(festivals)
    path = os.path.join(RAW_DIR, "festival_mapping.csv")
    df.to_csv(path, index=False)
    print(f"✅ Created festival_mapping.csv ({len(df)} occasions)")
    return df


def create_purpose_mapping():
    """
    Create purpose_mapping.csv with usage-to-fabric mappings.
    Based on e-commerce product categorization patterns (Flipkart/Amazon).
    """
    purposes = [
        {
            "purpose": "Daily Wear",
            "recommended_fabrics": "Cotton,Linen,Denim,Khadi,Modal,Bamboo,Rayon,Polyester",
            "priority_factor": "comfort",
            "activity_level": "Low",
            "description": "Everyday regular clothing for routine activities"
        },
        {
            "purpose": "Office",
            "recommended_fabrics": "Cotton,Linen,Polyester,Crepe,Modal,Tencel",
            "priority_factor": "comfort",
            "activity_level": "Low",
            "description": "Professional workplace attire"
        },
        {
            "purpose": "Sports",
            "recommended_fabrics": "Polyester,Nylon,Lycra,Spandex,Bamboo",
            "priority_factor": "durability",
            "activity_level": "High",
            "description": "Athletic and sports activities"
        },
        {
            "purpose": "Travel",
            "recommended_fabrics": "Cotton,Polyester,Nylon,Denim,Modal,Tencel,Lycra",
            "priority_factor": "durability",
            "activity_level": "Medium",
            "description": "Travel and journey clothing"
        },
        {
            "purpose": "Loungewear",
            "recommended_fabrics": "Cotton,Bamboo,Modal,Fleece,Muslin,Tencel",
            "priority_factor": "comfort",
            "activity_level": "Low",
            "description": "Relaxing at home, sleeping, casual comfort"
        },
        {
            "purpose": "Party",
            "recommended_fabrics": "Silk,Satin,Velvet,Georgette,Chiffon,Crepe,Lycra,Organza",
            "priority_factor": "style",
            "activity_level": "Medium",
            "description": "Party and nightlife clothing"
        },
        {
            "purpose": "Outdoor",
            "recommended_fabrics": "Nylon,Polyester,Denim,Hemp,Cotton,Lycra",
            "priority_factor": "durability",
            "activity_level": "High",
            "description": "Outdoor activities, hiking, camping"
        },
        {
            "purpose": "Work/Labor",
            "recommended_fabrics": "Denim,Cotton,Hemp,Polyester,Nylon,Khadi",
            "priority_factor": "durability",
            "activity_level": "High",
            "description": "Physical labor and manual work"
        },
        {
            "purpose": "Ethnic Wear",
            "recommended_fabrics": "Silk,Cotton,Khadi,Georgette,Chiffon,Brocade,Satin,Velvet,Organza",
            "priority_factor": "style",
            "activity_level": "Low",
            "description": "Traditional and ethnic clothing"
        },
        {
            "purpose": "Formal",
            "recommended_fabrics": "Cotton,Linen,Silk,Polyester,Crepe,Satin",
            "priority_factor": "style",
            "activity_level": "Low",
            "description": "Formal events, meetings, business"
        },
        {
            "purpose": "Beach",
            "recommended_fabrics": "Cotton,Linen,Rayon,Chiffon,Nylon,Lycra",
            "priority_factor": "breathability",
            "activity_level": "Medium",
            "description": "Beachwear and poolside clothing"
        },
        {
            "purpose": "Yoga/Meditation",
            "recommended_fabrics": "Cotton,Bamboo,Modal,Lycra,Spandex,Tencel",
            "priority_factor": "comfort",
            "activity_level": "Medium",
            "description": "Yoga, meditation, and mindful exercise"
        },
    ]

    df = pd.DataFrame(purposes)
    path = os.path.join(RAW_DIR, "purpose_mapping.csv")
    df.to_csv(path, index=False)
    print(f"✅ Created purpose_mapping.csv ({len(df)} purposes)")
    return df


if __name__ == "__main__":
    print("=" * 60)
    print("  AI Fabric Advisor — Dataset Generation")
    print("=" * 60)
    print()

    fabric_df = create_fabric_properties()
    weather_df = create_weather_categories()
    festival_df = create_festival_mapping()
    purpose_df = create_purpose_mapping()

    print()
    print("=" * 60)
    print("  All datasets created successfully!")
    print(f"  Output directory: {os.path.abspath(RAW_DIR)}")
    print("=" * 60)
