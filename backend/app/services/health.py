from dataclasses import dataclass

from neo4j import GraphDatabase
from sqlalchemy import text

from app.core.config import get_settings
from app.db import engine


@dataclass(frozen=True)
class DependencyStatus:
    mysql: bool
    neo4j: bool

    @property
    def ready(self) -> bool:
        return self.mysql and self.neo4j

    def as_dict(self) -> dict[str, object]:
        return {
            "status": "ready" if self.ready else "not_ready",
            "dependencies": {
                "mysql": "ok" if self.mysql else "unavailable",
                "neo4j": "ok" if self.neo4j else "unavailable",
            },
        }


def check_dependencies() -> DependencyStatus:
    settings = get_settings()
    mysql_ok = False
    neo4j_ok = False

    try:
        with engine.connect() as connection:
            mysql_ok = connection.execute(text("SELECT 1")).scalar_one() == 1
    except Exception:
        mysql_ok = False

    try:
        auth = (settings.neo4j_user, settings.neo4j_password)
        with GraphDatabase.driver(settings.neo4j_uri, auth=auth) as driver:
            record = driver.execute_query("RETURN 1 AS ok", database_="neo4j").records[0]
            neo4j_ok = record["ok"] == 1
    except Exception:
        neo4j_ok = False

    return DependencyStatus(mysql=mysql_ok, neo4j=neo4j_ok)
