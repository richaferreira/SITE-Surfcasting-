// Surfcasting Região dos Lagos
// Seed idempotente do motor de recomendação.
// Consultas parametrizadas de runtime ficam no serviço Python, não neste arquivo.
// Cada ponto e vírgula encerra uma consulta Cypher; por isso os relacionamentos
// fazem MATCH explícito dos nós persistidos antes de criar as arestas.

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

CREATE CONSTRAINT technique_key_unique IF NOT EXISTS
FOR (technique:Technique) REQUIRE technique.key IS UNIQUE;

CREATE CONSTRAINT equipment_key_unique IF NOT EXISTS
FOR (equipment:Equipment) REQUIRE equipment.key IS UNIQUE;

// Praia de Itaúna -> vento sudoeste -> água fria -> Anchova.
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

MERGE (technique:Technique {key: 'SURF_SPINNING'})
SET technique.name = 'Surf spinning com artificial',
    technique.description = 'Trabalho ativo de iscas artificiais em canais e zonas de passagem.';

MERGE (rod:Equipment {key: 'ROD_SURF_360'})
SET rod.name = 'Vara de surfcasting 3,60 m', rod.category = 'VARA';

MERGE (reel:Equipment {key: 'REEL_5000_8000'})
SET reel.name = 'Molinete tamanho 5000–8000', reel.category = 'MOLINETE';

MERGE (leader:Equipment {key: 'LEADER_ABRASION'})
SET leader.name = 'Leader resistente à abrasão', leader.category = 'LINHA';

MATCH (beach:Beach {slug: 'praia-de-itauna'})
MATCH (wind:WindCondition {key: 'SW_MODERATE'})
MATCH (water:WaterCondition {key: 'COLD_16_20'})
MATCH (tide:TideCondition {key: 'RISING'})
MATCH (species:Species {name: 'Anchova'})
MATCH (technique:Technique {key: 'SURF_SPINNING'})
MATCH (rod:Equipment {key: 'ROD_SURF_360'})
MATCH (reel:Equipment {key: 'REEL_5000_8000'})
MATCH (leader:Equipment {key: 'LEADER_ABRASION'})
MERGE (beach)-[:HAS_RELEVANT_CONDITION {weight: 0.70}]->(wind)
MERGE (wind)-[:COMMONLY_ASSOCIATED_WITH]->(water)
MERGE (water)-[:FAVORS {weight: 0.85}]->(species)
MERGE (tide)-[:FAVORS {weight: 0.75}]->(species)
MERGE (beach)-[:OBSERVED_TIDE_PATTERN]->(tide)
MERGE (species)-[:RECOMMENDS_TECHNIQUE]->(technique)
MERGE (technique)-[:USES_EQUIPMENT]->(rod)
MERGE (technique)-[:USES_EQUIPMENT]->(reel)
MERGE (technique)-[:USES_EQUIPMENT]->(leader);
