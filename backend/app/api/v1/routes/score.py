from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import Settings, get_settings
from app.api.dependencies.rate_limit import enforce_score_rate_limit
from app.core.exceptions import ExternalAPIError
from app.integrations.openweather import OpenWeatherClient
from app.integrations.stormglass import StormglassClient
from app.schemas.score import FishingScoreResponse
from app.services.fishing_score import FishingScoreService
from app.services.score_cache import score_cache

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
        cache=score_cache,
        cache_ttl_seconds=settings.score_cache_ttl_seconds,
        cache_max_entries=settings.score_cache_max_entries,
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
    rate_limit: Annotated[None, Depends(enforce_score_rate_limit)],
) -> FishingScoreResponse:
    del rate_limit
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
