from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class TideTrend(StrEnum):
    RISING = "rising"
    FALLING = "falling"
    SLACK = "slack"
    UNKNOWN = "unknown"


class MoonPhase(StrEnum):
    NEW = "new"
    WAXING = "waxing"
    FULL = "full"
    WANING = "waning"


@dataclass(frozen=True, slots=True)
class EnvironmentalConditions:
    sea_bearing_deg: float
    wind_speed_mps: float | None = None
    wind_direction_deg: float | None = None
    tide_trend: TideTrend = TideTrend.UNKNOWN
    wave_height_m: float | None = None
    wave_period_s: float | None = None
    water_temperature_c: float | None = None
    pressure_hpa: float | None = None
    moon_phase: MoonPhase = MoonPhase.WAXING


@dataclass(frozen=True, slots=True)
class ScoreResult:
    score: int
    label: str
    breakdown: dict[str, float]
    reasons: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "label": self.label,
            "breakdown": self.breakdown,
            "reasons": self.reasons,
        }


def angular_distance(first_deg: float, second_deg: float) -> float:
    """Return the smallest angle between two bearings."""
    return abs((first_deg - second_deg + 180.0) % 360.0 - 180.0)


def is_offshore_wind(
    wind_from_deg: float,
    sea_bearing_deg: float,
    tolerance_deg: float = 45.0,
) -> bool:
    """Detect a wind travelling from land toward the sea (vento terral).

    Weather providers report the direction *from* which the wind originates.
    The travel bearing is therefore the reported bearing plus 180 degrees.
    """
    wind_travel_bearing = (wind_from_deg + 180.0) % 360.0
    return angular_distance(wind_travel_bearing, sea_bearing_deg) <= tolerance_deg


def moon_phase_for(moment: datetime) -> MoonPhase:
    """Estimate the lunar phase from a known new-moon epoch.

    This is sufficient for the low-weight heuristic. A future astronomy adapter
    can replace it without changing the score contract.
    """
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    else:
        moment = moment.astimezone(timezone.utc)

    known_new_moon = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    synodic_month_days = 29.53058867
    lunar_age = ((moment - known_new_moon).total_seconds() / 86400.0) % synodic_month_days

    if lunar_age < 1.85 or lunar_age >= 27.68:
        return MoonPhase.NEW
    if lunar_age < 12.92:
        return MoonPhase.WAXING
    if lunar_age < 16.61:
        return MoonPhase.FULL
    return MoonPhase.WANING


def calculate_fishing_score(conditions: EnvironmentalConditions) -> ScoreResult:
    breakdown: dict[str, float] = {}
    reasons: list[str] = []

    # Wind: 30 points.
    if conditions.wind_speed_mps is None or conditions.wind_direction_deg is None:
        breakdown["wind"] = 10.0
        reasons.append("Vento indisponível; aplicado valor conservador.")
    else:
        offshore = is_offshore_wind(
            wind_from_deg=conditions.wind_direction_deg,
            sea_bearing_deg=conditions.sea_bearing_deg,
        )
        speed = conditions.wind_speed_mps
        if offshore and speed <= 8.0:
            breakdown["wind"] = 30.0
            reasons.append("Vento terral moderado favorece a leitura e o arremesso.")
        elif offshore and speed <= 12.0:
            breakdown["wind"] = 23.0
            reasons.append("Vento terral presente, porém já exige atenção à intensidade.")
        elif speed <= 8.0:
            breakdown["wind"] = 16.0
            reasons.append("Vento moderado, mas sem alinhamento terral ideal.")
        elif speed <= 14.0:
            breakdown["wind"] = 9.0
            reasons.append("Vento forte pode dificultar arremessos e leitura da praia.")
        else:
            breakdown["wind"] = 3.0
            reasons.append("Vento muito forte reduz a segurança e a eficiência da pescaria.")

    # Tide: 25 points.
    tide_points = {
        TideTrend.RISING: 25.0,
        TideTrend.SLACK: 12.0,
        TideTrend.FALLING: 8.0,
        TideTrend.UNKNOWN: 8.0,
    }
    breakdown["tide"] = tide_points[conditions.tide_trend]
    tide_reason = {
        TideTrend.RISING: "Maré enchendo recebe o maior peso desta versão inicial.",
        TideTrend.SLACK: "Maré próxima da virada recebe pontuação intermediária.",
        TideTrend.FALLING: "Maré vazando recebe peso menor na heurística geral.",
        TideTrend.UNKNOWN: "Tendência da maré indisponível; aplicado valor conservador.",
    }
    reasons.append(tide_reason[conditions.tide_trend])

    # Swell: 20 points (12 height + 8 period).
    if conditions.wave_height_m is None:
        height_points = 5.0
    elif 0.6 <= conditions.wave_height_m <= 1.8:
        height_points = 12.0
    elif 0.3 <= conditions.wave_height_m <= 2.3:
        height_points = 8.0
    elif conditions.wave_height_m > 2.8:
        height_points = 1.0
        reasons.append("Ondas muito altas exigem cautela e reduzem o score.")
    else:
        height_points = 4.0

    if conditions.wave_period_s is None:
        period_points = 3.0
    elif 7.0 <= conditions.wave_period_s <= 14.0:
        period_points = 8.0
    elif 5.0 <= conditions.wave_period_s <= 17.0:
        period_points = 5.0
    else:
        period_points = 2.0
    breakdown["swell"] = height_points + period_points

    # Water temperature: 10 points. This generic range will later vary by species.
    if conditions.water_temperature_c is None:
        breakdown["water_temperature"] = 5.0
    elif 18.0 <= conditions.water_temperature_c <= 25.0:
        breakdown["water_temperature"] = 10.0
    elif 15.0 <= conditions.water_temperature_c <= 28.0:
        breakdown["water_temperature"] = 7.0
    else:
        breakdown["water_temperature"] = 3.0

    # Pressure: 10 points.
    if conditions.pressure_hpa is None:
        breakdown["pressure"] = 5.0
    elif 1010.0 <= conditions.pressure_hpa <= 1025.0:
        breakdown["pressure"] = 10.0
    elif 1000.0 <= conditions.pressure_hpa <= 1030.0:
        breakdown["pressure"] = 7.0
    else:
        breakdown["pressure"] = 3.0

    # Moon: 5 points. Kept deliberately small until calibrated with local catches.
    moon_points = {
        MoonPhase.NEW: 5.0,
        MoonPhase.FULL: 4.0,
        MoonPhase.WAXING: 2.0,
        MoonPhase.WANING: 2.0,
    }
    breakdown["moon"] = moon_points[conditions.moon_phase]

    score = round(sum(breakdown.values()))
    score = max(0, min(100, score))
    if score >= 75:
        label = "excelente"
    elif score >= 60:
        label = "bom"
    elif score >= 40:
        label = "moderado"
    else:
        label = "baixo"

    return ScoreResult(score=score, label=label, breakdown=breakdown, reasons=reasons)
