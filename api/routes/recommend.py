"""
Recommendation API Route — /recommend endpoint.
"""

from fastapi import APIRouter, HTTPException
from api.schemas.models import RecommendRequest, RecommendResponse, FabricRecommendation, OptionsResponse
from api.services.recommendation_service import get_recommendation_service

router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_fabric(request: RecommendRequest):
    """Get fabric recommendations based on weather, festival, and purpose."""
    try:
        service = get_recommendation_service()
        results = service.get_recommendations(
            weather=request.weather,
            festival=request.festival,
            purpose=request.purpose,
            top_n=request.top_n,
        )

        recommendations = [FabricRecommendation(**r) for r in results]
        explanation = service.generate_explanation(
            request.weather, request.festival, request.purpose, results
        )

        return RecommendResponse(
            success=True,
            recommendations=recommendations,
            query={
                "weather": request.weather,
                "festival": request.festival,
                "purpose": request.purpose,
            },
            explanation=explanation,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/options", response_model=OptionsResponse)
async def get_options():
    """Get valid input options for dropdowns."""
    service = get_recommendation_service()
    options = service.get_options()
    return OptionsResponse(**options)
