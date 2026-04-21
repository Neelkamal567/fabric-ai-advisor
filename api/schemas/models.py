"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class RecommendRequest(BaseModel):
    """Request body for /recommend endpoint."""
    weather: str = Field(..., description="Weather condition", examples=["summer", "winter", "rainy"])
    festival: str = Field(..., description="Festival or occasion", examples=["Wedding", "Diwali", "None"])
    purpose: str = Field(..., description="Usage purpose", examples=["Daily Wear", "Office", "Party"])
    top_n: int = Field(default=5, ge=1, le=10, description="Number of recommendations")


class FabricRecommendation(BaseModel):
    """Single fabric recommendation."""
    fabric_type: str
    suitability_score: float = 0.0
    combined_score: float = 0.0
    comfort_level: int = 0
    durability: int = 0
    breathability: int = 0
    sustainability_score: int = 0
    cost_category: str = ""
    weight: str = ""
    moisture_wicking: str = ""
    match_strength: int = 0
    ml_confidence: float = 0.0
    why_this_fabric: str = ""
    image_url: str = ""
    advantages: List[str] = []
    disadvantages: List[str] = []
    care_instructions: str = ""


class RecommendResponse(BaseModel):
    """Response body for /recommend endpoint."""
    success: bool
    recommendations: List[FabricRecommendation]
    query: dict
    explanation: str = ""


class ChatRequest(BaseModel):
    """Request body for /chat endpoint."""
    message: str = Field(..., min_length=1, description="User message")
    history: List[dict] = Field(default_factory=list, description="Conversation history")
    ui_context: Optional[dict] = Field(default_factory=dict, description="Active UI dropdown states")


class ChatResponse(BaseModel):
    """Response body for /chat endpoint."""
    success: bool
    reply: str
    recommendations: Optional[List[FabricRecommendation]] = None
    history: List[dict] = []


class OptionsResponse(BaseModel):
    """Response body for /options endpoint."""
    weathers: List[str]
    festivals: List[str]
    purposes: List[str]


class HealthResponse(BaseModel):
    """Response body for /health endpoint."""
    status: str
    model_loaded: bool
    dataset_loaded: bool
    gemini_available: bool
