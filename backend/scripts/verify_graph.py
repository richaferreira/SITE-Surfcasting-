from neo4j import GraphDatabase

from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    try:
        records, _, _ = driver.execute_query(
            """
            MATCH (b:Beach)
            OPTIONAL MATCH (b)-[:HAS_RELEVANT_CONDITION]->(w:WindCondition)
            WITH b, count(w) AS windCount
            WITH count(b) AS beaches,
                 sum(CASE WHEN windCount > 0 THEN 1 ELSE 0 END) AS connectedBeaches
            CALL { MATCH (s:Species) RETURN count(s) AS species }
            CALL {
                MATCH (t:Technique)
                OPTIONAL MATCH (t)-[:USES_EQUIPMENT]->(e:Equipment)
                WITH t, count(e) AS equipmentCount
                RETURN count(t) AS techniques, min(equipmentCount) AS minEquipmentPerTechnique
            }
            CALL { MATCH (e:Equipment) RETURN count(e) AS equipment }
            RETURN beaches, connectedBeaches, species, techniques,
                   minEquipmentPerTechnique, equipment
            """,
            database_="neo4j",
        )
        if not records:
            raise RuntimeError("Neo4j não retornou resultado para a verificação do seed.")

        row = records[0]
        values = {
            "beaches": int(row["beaches"]),
            "connected_beaches": int(row["connectedBeaches"]),
            "species": int(row["species"]),
            "techniques": int(row["techniques"]),
            "min_equipment_per_technique": int(row["minEquipmentPerTechnique"] or 0),
            "equipment": int(row["equipment"]),
        }
        expected = {
            "beaches": 8,
            "connected_beaches": 8,
            "species": 4,
            "techniques": 4,
            "min_equipment_per_technique": 3,
            "equipment": 7,
        }
        failures = [
            f"{key}={values[key]} (mínimo esperado {minimum})"
            for key, minimum in expected.items()
            if values[key] < minimum
        ]
        if failures:
            raise RuntimeError("Seed Neo4j incompleto: " + "; ".join(failures))

        print(
            "GRAPH_OK "
            + " ".join(f"{key}={value}" for key, value in values.items())
        )
    finally:
        driver.close()


if __name__ == "__main__":
    main()
