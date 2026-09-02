from dataclasses import dataclass

from neo4j import GraphDatabase

from app.core.config import get_settings

settings = get_settings()


@dataclass(frozen=True)
class SpeciesRecommendation:
    species: str
    relevance: float
    technique: str | None
    equipment: tuple[str, ...]


def degrees_to_compass(degrees: float) -> str:
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return directions[int((degrees % 360 + 22.5) // 45) % 8]


def recommend_species(
    beach_slug: str,
    wind_direction_deg: float,
    wind_speed_mps: float,
    water_temperature_c: float,
    tide_key: str,
) -> list[SpeciesRecommendation]:
    query = """
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
    OPTIONAL MATCH (species)-[:RECOMMENDS_TECHNIQUE]->(technique:Technique)
    OPTIONAL MATCH (technique)-[:USES_EQUIPMENT]->(equipment:Equipment)
    WITH species, technique, collect(DISTINCT equipment.name) AS equipmentNames,
         beachWind.weight + waterSpecies.weight + coalesce(tideSpecies.weight, 0.0) AS relevance
    RETURN species.name AS species,
           technique.name AS technique,
           [name IN equipmentNames WHERE name IS NOT NULL] AS equipment,
           round(relevance * 100) / 100 AS relevance
    ORDER BY relevance DESC
    LIMIT 10
    """
    auth = (settings.neo4j_user, settings.neo4j_password)
    with GraphDatabase.driver(settings.neo4j_uri, auth=auth) as driver:
        records = driver.execute_query(
            query,
            beachSlug=beach_slug,
            windDirection=degrees_to_compass(wind_direction_deg),
            windSpeedMps=wind_speed_mps,
            waterTemperatureC=water_temperature_c,
            tideKey=tide_key.upper(),
            database_="neo4j",
        ).records
    return [
        SpeciesRecommendation(
            species=record["species"],
            relevance=float(record["relevance"]),
            technique=record["technique"],
            equipment=tuple(record["equipment"] or []),
        )
        for record in records
    ]
