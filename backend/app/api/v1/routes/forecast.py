from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.rate_limit import enforce_telemetry_rate_limit
from app.core.config import Settings, get_settings
from app.core.exceptions import ExternalAPIError
from app.integrations.stormglass import StormglassClient
from app.schemas.forecast import MarineForecastResponse
from app.services.marine_forecast import MarineForecastService


router = APIRouter(prefix="/forecast", tags=["Telemetria oceanográfica"])


def get_forecast_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> MarineForecastService:
    return MarineForecastService(
        stormglass=StormglassClient(
            api_key=settings.stormglass_api_key,
            timeout_seconds=settings.request_timeout_seconds,
        )
    )


@router.get("", response_model=MarineForecastResponse)
def get_marine_forecast(
    latitude: Annotated[float, Query(ge=-90, le=90)],
    longitude: Annotated[float, Query(ge=-180, le=180)],
    service: Annotated[MarineForecastService, Depends(get_forecast_service)],
    rate_limit: Annotated[None, Depends(enforce_telemetry_rate_limit)],
    hours: Annotated[int, Query(ge=6, le=48)] = 24,
) -> MarineForecastResponse:
    del rate_limit
    try:
        result = service.get_forecast(
            latitude=latitude,
            longitude=longitude,
            hours=hours,
        )
    except ExternalAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return MarineForecastResponse.model_validate(result)
