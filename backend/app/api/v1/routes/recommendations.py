from fastapi import APIRouter, HTTPException, Query
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app.services.recommendations import recommend_species

router = APIRouter(prefix="/recommendations", tags=["Recomendações"])


@router.get("/{beach_slug}")
def recommendations(
    beach_slug: str,
    wind_direction_deg: float = Query(ge=0, lt=360),
    wind_speed_mps: float = Query(ge=0, le=80),
    water_temperature_c: float = Query(ge=-2, le=45),
    tide_key: str = Query(default="RISING", pattern=r"^(RISING|FALLING|HIGH|LOW)$"),
) -> dict[str, object]:
    try:
        items = recommend_species(
            beach_slug=beach_slug,
            wind_direction_deg=wind_direction_deg,
            wind_speed_mps=wind_speed_mps,
            water_temperature_c=water_temperature_c,
            tide_key=tide_key,
        )
    except (ServiceUnavailable, Neo4jError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Motor de recomendação temporariamente indisponível.",
        ) from exc

    return {
        "beach_slug": beach_slug,
        "recommendations": [
            {"species": item.species, "relevance": item.relevance} for item in items
        ],
        "explanation": (
            "Resultado derivado das relações entre praia, vento, temperatura da água, maré e espécie no Neo4j."
        ),
    }
