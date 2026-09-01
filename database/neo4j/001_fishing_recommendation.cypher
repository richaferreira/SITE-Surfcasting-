// Surfcasting Região dos Lagos
// Modelo inicial de relações para o motor de recomendação.

CREATE CONSTRAINT beach_slug_unique IF NOT EXISTS
FOR (beach:Beach) REQUIRE beach.slug IS UNIQUE;

CREATE CONSTRAINT species_name_unique IF NOT EXISTS
FOR (species:Species) REQUIRE species.name IS UNIQUE;

CREATE CONSTRAINT wind_key_unique IF NOT EXISTS
FOR (wind:WindCondition) REQUIRE wind.key IS UNIQUE;

CREATE CONSTRAINT water_key_unique IF NOT EXISTS
FOR (water:WaterCondition) REQUIRE water.key IS UNIQUE;

CREATE CONSTRAINT tide_key_unique IF NOT EXISTS
FOR (tide:TideCondition) REQUIRE tide.key IS UNIQUE;

// Exemplo: Praia de Itaúna -> vento sudoeste -> água fria -> anchova.
MERGE (beach:Beach {slug: 'praia-de-itauna'})
SET beach.name = 'Praia de Itaúna',
    beach.city = 'Saquarema',
    beach.state = 'RJ';

MERGE (wind:WindCondition {key: 'SW_MODERATE'})
SET wind.direction = 'SW',
    wind.minSpeedMps = 2.0,
    wind.maxSpeedMps = 8.0;

MERGE (water:WaterCondition {key: 'COLD_16_20'})
SET water.label = 'Água fria',
    water.minTemperatureC = 16.0,
    water.maxTemperatureC = 20.0;

MERGE (tide:TideCondition {key: 'RISING'})
SET tide.label = 'Maré enchendo';

MERGE (species:Species {name: 'Anchova'})
SET species.scientificName = 'Pomatomus saltatrix';

MERGE (beach)-[:HAS_RELEVANT_CONDITION {weight: 0.70}]->(wind)
MERGE (wind)-[:COMMONLY_ASSOCIATED_WITH]->(water)
MERGE (water)-[:FAVORS {weight: 0.85}]->(species)
MERGE (tide)-[:FAVORS {weight: 0.75}]->(species)
MERGE (beach)-[:OBSERVED_TIDE_PATTERN]->(tide);

// Exemplo de consulta de recomendação.
// Os parâmetros devem vir do serviço Python, nunca de concatenação de strings.
// :param beachSlug => 'praia-de-itauna';
// :param windDirection => 'SW';
// :param windSpeedMps => 5.0;
// :param waterTemperatureC => 18.0;
// :param tideKey => 'RISING';

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
       round(relevance * 100) / 100 AS relevance
ORDER BY relevance DESC;
