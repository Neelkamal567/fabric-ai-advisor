"""
Chat API Route — /chat endpoint.
"""

from fastapi import APIRouter, HTTPException
from api.schemas.models import ChatRequest, ChatResponse, FabricRecommendation
from api.services.chat_service import get_chat_service
from api.services.recommendation_service import get_recommendation_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return AI response with optional recommendations."""
    try:
        chat_service = get_chat_service()
        rec_service = get_recommendation_service()

        # Try to extract recommendation context from the message
        recommendation_context = ""
        recommendations = None
        message_lower = request.message.lower()

        # Parse weather, festival, purpose from natural language
        weather = _extract_value(message_lower, [
            "summer", "winter", "rainy", "humid", "autumn"
        ])
        festival = _extract_value(message_lower, [
            "wedding", "diwali", "eid", "christmas", "holi", "pongal",
            "onam", "navratri", "new year", "interview", "graduation",
            "date night", "durga puja"
        ])
        purpose = _extract_value(message_lower, [
            "daily wear", "office", "sports", "travel", "loungewear",
            "party", "outdoor", "work", "ethnic wear", "formal",
            "beach", "yoga"
        ])

        # If we detected intent, get recommendations
        if weather or festival or purpose:
            w = weather or "summer"
            f = _title_case_match(festival, rec_service.get_options().get("festivals", [])) or "None"
            p = _title_case_match(purpose, rec_service.get_options().get("purposes", [])) or "Daily Wear"

            results = rec_service.get_recommendations(w, f, p, top_n=3)
            if results:
                recommendations = [FabricRecommendation(**r) for r in results]
                recommendation_context = rec_service.generate_explanation(w, f, p, results)

        # Get chat response
        result = await chat_service.chat(
            message=request.message,
            history=request.history,
            recommendation_context=recommendation_context,
            ui_context=request.ui_context
        )

        return ChatResponse(
            success=True,
            reply=result["reply"],
            recommendations=recommendations,
            history=result["history"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _extract_value(text: str, options: list) -> str:
    """Extract a matching value from text."""
    for opt in options:
        if opt.lower() in text:
            return opt
    return ""


def _title_case_match(value: str, valid_options: list) -> str:
    """Match a value case-insensitively against valid options."""
    if not value:
        return ""
    for opt in valid_options:
        if opt.lower() == value.lower():
            return opt
    # Try partial match
    for opt in valid_options:
        if value.lower() in opt.lower():
            return opt
    return ""
