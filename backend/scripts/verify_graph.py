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
            MATCH (species:Species {name: 'Anchova'})
                  -[:RECOMMENDS_TECHNIQUE]->(technique:Technique {key: 'SURF_SPINNING'})
            OPTIONAL MATCH (technique)-[:USES_EQUIPMENT]->(equipment:Equipment)
            RETURN count(DISTINCT technique) AS techniques,
                   count(DISTINCT equipment) AS equipment
            """,
            database_="neo4j",
        )
        if not records:
            raise RuntimeError("Neo4j não retornou resultado para a verificação do seed.")

        techniques = int(records[0]["techniques"])
        equipment = int(records[0]["equipment"])
        if techniques != 1 or equipment < 3:
            raise RuntimeError(
                "Seed Neo4j incompleto: "
                f"techniques={techniques}, equipment={equipment}; esperado techniques=1 e equipment>=3."
            )
        print(f"GRAPH_OK techniques={techniques} equipment={equipment}")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
