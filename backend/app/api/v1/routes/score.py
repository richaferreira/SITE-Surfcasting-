from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import Settings, get_settings
from app.core.exceptions import ExternalAPIError
from app.integrations.openweather import OpenWeatherClient
from app.integrations.stormglass import StormglassClient
from app.schemas.score import FishingScoreResponse
from app.services.fishing_score import FishingScoreService

router = APIRouter(prefix="/fishing-score", tags=["Score de Pesca"])


def get_score_service(settings: Annotated[Settings, Depends(get_settings)]) -> FishingScoreService:
    return FishingScoreService(
        openweather=OpenWeatherClient(
            api_key=settings.openweather_api_key,
            timeout_seconds=settings.request_timeout_seconds,
        ),
        stormglass=StormglassClient(
            api_key=settings.stormglass_api_key,
            timeout_seconds=settings.request_timeout_seconds,
        ),
    )


@router.get("", response_model=FishingScoreResponse)
def calculate_fishing_score(
    latitude: Annotated[float, Query(ge=-90, le=90)],
    longitude: Annotated[float, Query(ge=-180, le=180)],
    sea_bearing_deg: Annotated[
        float,
        Query(
            ge=0,
            lt=360,
            description="Direção, em graus, da faixa de areia para o mar.",
        ),
    ],
    service: Annotated[FishingScoreService, Depends(get_score_service)],
) -> FishingScoreResponse:
    try:
        result = service.calculate(
            latitude=latitude,
            longitude=longitude,
            sea_bearing_deg=sea_bearing_deg,
        )
    except ExternalAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return FishingScoreResponse.model_validate(result)
