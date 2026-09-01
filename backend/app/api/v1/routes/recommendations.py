from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.config import Settings, get_settings
from app.domain.score import TideTrend
from app.integrations.neo4j_recommendations import (
    Neo4jRecommendationRepository,
    direction_to_compass,
    get_neo4j_driver,
)
from app.schemas.recommendation import RecommendationListResponse


router = APIRouter(prefix="/beaches", tags=["Recomendações"])


@router.get("/{beach_slug}/recommendations", response_model=RecommendationListResponse)
def recommend_species(
    beach_slug: str,
    wind_direction_deg: Annotated[float, Query(ge=0, lt=360)],
    wind_speed_mps: Annotated[float, Query(ge=0, le=80)],
    water_temperature_c: Annotated[float, Query(ge=-2, le=40)],
    tide: TideTrend,
    settings: Annotated[Settings, Depends(get_settings)],
) -> RecommendationListResponse:
    driver = get_neo4j_driver(
        settings.neo4j_uri,
        settings.neo4j_user,
        settings.neo4j_password,
    )
    items = Neo4jRecommendationRepository(driver).recommend(
        beach_slug=beach_slug,
        wind_direction_deg=wind_direction_deg,
        wind_speed_mps=wind_speed_mps,
        water_temperature_c=water_temperature_c,
        tide_key=tide.value.upper(),
    )
    return RecommendationListResponse(
        beach_slug=beach_slug,
        wind_direction=direction_to_compass(wind_direction_deg),
        items=items,
    )

