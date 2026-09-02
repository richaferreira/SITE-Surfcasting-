// Surfcasting Região dos Lagos
// Seed editorial idempotente do motor de recomendação.
// O grafo sugere combinações técnicas; não substitui leitura local de mar, segurança ou regulamentação.
// Cada ponto e vírgula encerra uma consulta Cypher, portanto cada bloco relacional faz MATCH explícito.

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

// Praias do catálogo inicial.
MERGE (n:Beach {slug:'praia-de-itauna'}) SET n.name='Praia de Itaúna', n.city='Saquarema', n.state='RJ';
MERGE (n:Beach {slug:'praia-da-vila-saquarema'}) SET n.name='Praia da Vila', n.city='Saquarema', n.state='RJ';
MERGE (n:Beach {slug:'praia-de-jacone'}) SET n.name='Praia de Jaconé', n.city='Saquarema', n.state='RJ';
MERGE (n:Beach {slug:'praia-de-barra-nova-saquarema'}) SET n.name='Praia de Barra Nova', n.city='Saquarema', n.state='RJ';
MERGE (n:Beach {slug:'praia-de-massambaba'}) SET n.name='Praia de Massambaba', n.city='Arraial do Cabo', n.state='RJ';
MERGE (n:Beach {slug:'praia-grande-arraial-do-cabo'}) SET n.name='Praia Grande', n.city='Arraial do Cabo', n.state='RJ';
MERGE (n:Beach {slug:'praia-do-foguete'}) SET n.name='Praia do Foguete', n.city='Cabo Frio', n.state='RJ';
MERGE (n:Beach {slug:'praia-do-pero'}) SET n.name='Praia do Peró', n.city='Cabo Frio', n.state='RJ';

// Condições ambientais amplas usadas pelo primeiro grafo editorial.
MERGE (n:WindCondition {key:'SW_MODERATE'}) SET n.direction='SW', n.minSpeedMps=2.0, n.maxSpeedMps=8.0;
MERGE (n:WindCondition {key:'E_MODERATE'}) SET n.direction='E', n.minSpeedMps=2.0, n.maxSpeedMps=8.0;
MERGE (n:WindCondition {key:'NE_MODERATE'}) SET n.direction='NE', n.minSpeedMps=1.0, n.maxSpeedMps=7.0;

MERGE (n:WaterCondition {key:'COLD_16_20'}) SET n.label='Água fria', n.minTemperatureC=16.0, n.maxTemperatureC=20.5;
MERGE (n:WaterCondition {key:'MILD_19_24'}) SET n.label='Água amena', n.minTemperatureC=19.0, n.maxTemperatureC=24.5;
MERGE (n:WaterCondition {key:'WARM_22_28'}) SET n.label='Água mais quente', n.minTemperatureC=22.0, n.maxTemperatureC=28.0;

MERGE (n:TideCondition {key:'RISING'}) SET n.label='Maré enchendo';
MERGE (n:TideCondition {key:'FALLING'}) SET n.label='Maré vazando';

// Espécies costeiras comuns no repertório editorial de surfcasting.
MERGE (n:Species {name:'Anchova'}) SET n.scientificName='Pomatomus saltatrix';
MERGE (n:Species {name:'Pampo'}) SET n.scientificName='Trachinotus spp.';
MERGE (n:Species {name:'Corvina'}) SET n.scientificName='Micropogonias furnieri';
MERGE (n:Species {name:'Robalo'}) SET n.scientificName='Centropomus spp.';

// Técnicas.
MERGE (n:Technique {key:'SURF_SPINNING'}) SET n.name='Surf spinning com artificial', n.description='Trabalho ativo de artificiais em canais e zonas de passagem.';
MERGE (n:Technique {key:'BOTTOM_SURF'}) SET n.name='Surfcasting de fundo', n.description='Isca natural apresentada no fundo, com montagem compatível com corrente e arrebentação.';
MERGE (n:Technique {key:'LONG_CAST_BOTTOM'}) SET n.name='Long cast de fundo', n.description='Arremesso mais longo buscando canais e bordas de bancos de areia.';
MERGE (n:Technique {key:'LIVE_BAIT'}) SET n.name='Isca natural em zona de canal', n.description='Apresentação controlada de isca natural em canal ou água estruturada.';

// Equipamentos editoriais genéricos, sem vínculo comercial.
MERGE (n:Equipment {key:'ROD_SURF_360'}) SET n.name='Vara de surfcasting 3,60 m', n.category='VARA';
MERGE (n:Equipment {key:'ROD_SURF_420'}) SET n.name='Vara de surfcasting 4,20 m', n.category='VARA';
MERGE (n:Equipment {key:'REEL_5000_8000'}) SET n.name='Molinete tamanho 5000–8000', n.category='MOLINETE';
MERGE (n:Equipment {key:'LEADER_ABRASION'}) SET n.name='Leader resistente à abrasão', n.category='LINHA';
MERGE (n:Equipment {key:'MAINLINE_SURF'}) SET n.name='Linha principal compatível com surfcasting', n.category='LINHA';
MERGE (n:Equipment {key:'SINKER_HOLD'}) SET n.name='Chumbada adequada à corrente e ao fundo', n.category='TERMINAL';
MERGE (n:Equipment {key:'HOOK_COASTAL'}) SET n.name='Anzol dimensionado à espécie e isca', n.category='TERMINAL';

// Vento -> faixa térmica.
MATCH (w:WindCondition {key:'SW_MODERATE'}), (water:WaterCondition {key:'COLD_16_20'}) MERGE (w)-[:COMMONLY_ASSOCIATED_WITH]->(water);
MATCH (w:WindCondition {key:'E_MODERATE'}), (water:WaterCondition {key:'MILD_19_24'}) MERGE (w)-[:COMMONLY_ASSOCIATED_WITH]->(water);
MATCH (w:WindCondition {key:'NE_MODERATE'}), (water:WaterCondition {key:'WARM_22_28'}) MERGE (w)-[:COMMONLY_ASSOCIATED_WITH]->(water);

// Água -> espécies.
MATCH (w:WaterCondition {key:'COLD_16_20'}), (s:Species {name:'Anchova'}) MERGE (w)-[:FAVORS {weight:0.85}]->(s);
MATCH (w:WaterCondition {key:'COLD_16_20'}), (s:Species {name:'Corvina'}) MERGE (w)-[:FAVORS {weight:0.55}]->(s);
MATCH (w:WaterCondition {key:'MILD_19_24'}), (s:Species {name:'Corvina'}) MERGE (w)-[:FAVORS {weight:0.85}]->(s);
MATCH (w:WaterCondition {key:'MILD_19_24'}), (s:Species {name:'Pampo'}) MERGE (w)-[:FAVORS {weight:0.75}]->(s);
MATCH (w:WaterCondition {key:'WARM_22_28'}), (s:Species {name:'Pampo'}) MERGE (w)-[:FAVORS {weight:0.80}]->(s);
MATCH (w:WaterCondition {key:'WARM_22_28'}), (s:Species {name:'Robalo'}) MERGE (w)-[:FAVORS {weight:0.80}]->(s);

// Maré -> espécies.
MATCH (t:TideCondition {key:'RISING'}), (s:Species {name:'Anchova'}) MERGE (t)-[:FAVORS {weight:0.75}]->(s);
MATCH (t:TideCondition {key:'RISING'}), (s:Species {name:'Pampo'}) MERGE (t)-[:FAVORS {weight:0.65}]->(s);
MATCH (t:TideCondition {key:'RISING'}), (s:Species {name:'Robalo'}) MERGE (t)-[:FAVORS {weight:0.70}]->(s);
MATCH (t:TideCondition {key:'FALLING'}), (s:Species {name:'Corvina'}) MERGE (t)-[:FAVORS {weight:0.65}]->(s);
MATCH (t:TideCondition {key:'FALLING'}), (s:Species {name:'Robalo'}) MERGE (t)-[:FAVORS {weight:0.55}]->(s);

// Espécie -> técnica.
MATCH (s:Species {name:'Anchova'}), (t:Technique {key:'SURF_SPINNING'}) MERGE (s)-[:RECOMMENDS_TECHNIQUE]->(t);
MATCH (s:Species {name:'Pampo'}), (t:Technique {key:'BOTTOM_SURF'}) MERGE (s)-[:RECOMMENDS_TECHNIQUE]->(t);
MATCH (s:Species {name:'Corvina'}), (t:Technique {key:'LONG_CAST_BOTTOM'}) MERGE (s)-[:RECOMMENDS_TECHNIQUE]->(t);
MATCH (s:Species {name:'Robalo'}), (t:Technique {key:'LIVE_BAIT'}) MERGE (s)-[:RECOMMENDS_TECHNIQUE]->(t);

// Técnica -> equipamento.
MATCH (t:Technique {key:'SURF_SPINNING'}), (e:Equipment {key:'ROD_SURF_360'}) MERGE (t)-[:USES_EQUIPMENT]->(e);
MATCH (t:Technique {key:'SURF_SPINNING'}), (e:Equipment {key:'REEL_5000_8000'}) MERGE (t)-[:USES_EQUIPMENT]->(e);
MATCH (t:Technique {key:'SURF_SPINNING'}), (e:Equipment {key:'LEADER_ABRASION'}) MERGE (t)-[:USES_EQUIPMENT]->(e);
MATCH (t:Technique {key:'BOTTOM_SURF'}), (e:Equipment {key:'ROD_SURF_360'}) MERGE (t)-[:USES_EQUIPMENT]->(e);
MATCH (t:Technique {key:'BOTTOM_SURF'}), (e:Equipment {key:'SINKER_HOLD'}) MERGE (t)-[:USES_EQUIPMENT]->(e);
MATCH (t:Technique {key:'BOTTOM_SURF'}), (e:Equipment {key:'HOOK_COASTAL'}) MERGE (t)-[:USES_EQUIPMENT]->(e);
MATCH (t:Technique {key:'LONG_CAST_BOTTOM'}), (e:Equipment {key:'ROD_SURF_420'}) MERGE (t)-[:USES_EQUIPMENT]->(e);
MATCH (t:Technique {key:'LONG_CAST_BOTTOM'}), (e:Equipment {key:'MAINLINE_SURF'}) MERGE (t)-[:USES_EQUIPMENT]->(e);
MATCH (t:Technique {key:'LONG_CAST_BOTTOM'}), (e:Equipment {key:'SINKER_HOLD'}) MERGE (t)-[:USES_EQUIPMENT]->(e);
MATCH (t:Technique {key:'LIVE_BAIT'}), (e:Equipment {key:'ROD_SURF_360'}) MERGE (t)-[:USES_EQUIPMENT]->(e);
MATCH (t:Technique {key:'LIVE_BAIT'}), (e:Equipment {key:'LEADER_ABRASION'}) MERGE (t)-[:USES_EQUIPMENT]->(e);
MATCH (t:Technique {key:'LIVE_BAIT'}), (e:Equipment {key:'HOOK_COASTAL'}) MERGE (t)-[:USES_EQUIPMENT]->(e);

// Praias -> condições e marés editoriais iniciais.
MATCH (b:Beach), (r:TideCondition {key:'RISING'}) MERGE (b)-[:OBSERVED_TIDE_PATTERN]->(r);
MATCH (b:Beach), (f:TideCondition {key:'FALLING'}) MERGE (b)-[:OBSERVED_TIDE_PATTERN]->(f);
MATCH (b:Beach), (w:WindCondition {key:'SW_MODERATE'}) WHERE b.slug <> 'praia-do-pero' MERGE (b)-[:HAS_RELEVANT_CONDITION {weight:0.60}]->(w);
MATCH (b:Beach), (w:WindCondition {key:'E_MODERATE'}) MERGE (b)-[:HAS_RELEVANT_CONDITION {weight:0.65}]->(w);
MATCH (b:Beach {slug:'praia-do-pero'}), (w:WindCondition {key:'NE_MODERATE'}) MERGE (b)-[:HAS_RELEVANT_CONDITION {weight:0.65}]->(w);
