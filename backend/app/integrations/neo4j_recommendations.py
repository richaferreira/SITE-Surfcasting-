from __future__ import annotations

from functools import lru_cache
from time import perf_counter
from typing import Any

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError

from app.core.exceptions import DependencyUnavailableError
from app.monitoring import monitoring_registry


RECOMMENDATION_QUERY = """
MATCH (beach:Beach {slug: $beachSlug})
MATCH (beach)-[beachWind:HAS_RELEVANT_CONDITION]->(wind:WindCondition)
WHERE wind.direction = $windDirection
  AND $windSpeedMps >= wind.minSpeedMps
  AND $windSpeedMps <= wind.maxSpeedMps
MATCH (wind)-[:COMMONLY_ASSOCIATED_WITH]->(water:WaterCondition)
WHERE $waterTemperatureC >= water.minTemperatureC
  AND $waterTemperatureC <= water.maxTemperatureC
MATCH (water)-[waterSpecies:FAVORS]->(species:Species)
OPTIONAL MATCH (beach)-[:OBSERVED_TIDE_PATTERN]->(tide:TideCondition {key: $tideKey})
OPTIONAL MATCH (tide)-[tideSpecies:FAVORS]->(species)
WITH species,
     beachWind.weight + waterSpecies.weight + coalesce(tideSpecies.weight, 0.0) AS relevance
RETURN species.name AS recommendedSpecies,
       species.scientificName AS scientificName,
       round(relevance * 100) / 100 AS relevance
ORDER BY relevance DESC
LIMIT 10
"""


@lru_cache(maxsize=4)
def get_neo4j_driver(uri: str, user: str, password: str) -> Driver:
    return GraphDatabase.driver(uri, auth=(user, password))


def direction_to_compass(direction_deg: float) -> str:
    directions = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
    return directions[round((direction_deg % 360) / 45) % 8]


class Neo4jRecommendationRepository:
    def __init__(self, driver: Driver):
        self.driver = driver

    def recommend(
        self,
        *,
        beach_slug: str,
        wind_direction_deg: float,
        wind_speed_mps: float,
        water_temperature_c: float,
        tide_key: str,
    ) -> list[dict[str, Any]]:
        parameters = {
            "beachSlug": beach_slug,
            "windDirection": direction_to_compass(wind_direction_deg),
            "windSpeedMps": wind_speed_mps,
            "waterTemperatureC": water_temperature_c,
            "tideKey": tide_key,
        }
        started_at = perf_counter()
        success = False
        error_code: str | None = None
        try:
            with self.driver.session(database="neo4j") as session:
                records = session.run(RECOMMENDATION_QUERY, parameters)
                result = [
                    {
                        "species": str(record["recommendedSpecies"]),
                        "scientific_name": (
                            str(record["scientificName"])
                            if record.get("scientificName") is not None
                            else None
                        ),
                        "relevance": float(record["relevance"]),
                    }
                    for record in records
                ]
            success = True
            return result
        except (Neo4jError, OSError, ValueError, TypeError) as exc:
            error_code = "neo4j_error"
            raise DependencyUnavailableError(
                "O motor de recomendações está temporariamente indisponível."
            ) from exc
        finally:
            monitoring_registry.record_external(
                "Neo4j Recommendations",
                success=success,
                latency_ms=(perf_counter() - started_at) * 1000,
                status_code=None,
                error_code=error_code,
            )
