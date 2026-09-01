from datetime import datetime

from pydantic import BaseModel, Field


class ConditionsResponse(BaseModel):
    wind_speed_mps: float | None
    wind_direction_deg: float | None
    sea_bearing_deg: float
    wind_is_offshore: bool | None
    tide_trend: str
    wave_height_m: float | None
    wave_period_s: float | None
    water_temperature_c: float | None
    pressure_hpa: float | None
    moon_phase: str


class DataQualityResponse(BaseModel):
    is_sufficient: bool
    confidence_percentage: int = Field(ge=0, le=100)
    available_components: list[str]
    missing_components: list[str]


class FishingScoreResponse(BaseModel):
    score: int | None = Field(default=None, ge=0, le=100)
    label: str
    calculated_at: datetime
    conditions: ConditionsResponse
    breakdown: dict[str, float]
    reasons: list[str]
    warnings: list[str]
    data_quality: DataQualityResponse
