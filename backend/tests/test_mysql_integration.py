import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.models.enums import BeachProfile
from app.repositories.user import UserRepository
from app.schemas.beach import BeachCreate
from app.services.beach import BeachService


MYSQL_URL = os.getenv("TEST_MYSQL_URL")
pytestmark = pytest.mark.skipif(not MYSQL_URL, reason="TEST_MYSQL_URL não configurada")


def test_spatial_round_trip_and_archive_preserve_fishing_points() -> None:
    assert MYSQL_URL is not None
    engine = create_engine(MYSQL_URL, pool_pre_ping=True)

    with Session(engine, expire_on_commit=False) as session:
        session.execute(text("DELETE FROM pontos_pesca"))
        session.execute(text("DELETE FROM praias"))
        session.execute(text("DELETE FROM users"))
        session.execute(
            text(
                """
                INSERT INTO users (role_id, name, username, email, password_hash, is_active)
                SELECT id, 'Admin CI', 'admin-ci', 'admin-ci@example.com', 'not-used', TRUE
                FROM roles WHERE code = 'ADMIN'
                """
            )
        )
        session.commit()

        actor = UserRepository(session).get_by_username("admin-ci")
        assert actor is not None
        beach = BeachService(session).create(
            BeachCreate(
                name="Praia de Itaúna",
                city="Saquarema",
                latitude=-22.93,
                longitude=-42.49,
                sea_bearing_deg=160,
                beach_profile=BeachProfile.TOMBO,
                is_published=True,
            ),
            actor=actor,
        )

        latitude, longitude = session.execute(
            text(
                "SELECT ST_Latitude(location), ST_Longitude(location) "
                "FROM praias WHERE id = :beach_id"
            ),
            {"beach_id": beach.id},
        ).one()
        assert float(latitude) == pytest.approx(-22.93)
        assert float(longitude) == pytest.approx(-42.49)

        session.execute(
            text(
                """
                INSERT INTO pontos_pesca (
                    praia_id, name, slug, point_type, latitude, longitude, location, created_by
                ) VALUES (
                    :beach_id, 'Canal teste', 'canal-teste', 'CANAL_RETORNO',
                    -22.93, -42.49,
                    ST_GeomFromText('POINT(-42.49 -22.93)', 4326, 'axis-order=long-lat'),
                    :actor_id
                )
                """
            ),
            {"beach_id": beach.id, "actor_id": actor.id},
        )
        session.commit()

        BeachService(session).delete(beach.id, actor=actor)

        archived_at = session.scalar(
            text("SELECT deleted_at FROM praias WHERE id = :beach_id"),
            {"beach_id": beach.id},
        )
        points_count = session.scalar(
            text("SELECT COUNT(*) FROM pontos_pesca WHERE praia_id = :beach_id"),
            {"beach_id": beach.id},
        )
        assert archived_at is not None
        assert points_count == 1

        session.execute(text("DELETE FROM pontos_pesca"))
        session.execute(text("DELETE FROM praias"))
        session.execute(text("DELETE FROM users"))
        session.commit()

