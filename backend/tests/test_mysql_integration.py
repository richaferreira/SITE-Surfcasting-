import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.models.enums import (
    AccessibilityLevel,
    BeachProfile,
    FishingPointType,
    PostContentType,
    PostStatus,
)
from app.repositories.user import UserRepository
from app.schemas.beach import BeachCreate
from app.schemas.fishing_point import FishingPointCreate
from app.schemas.post import EquipmentSpecificationInput, PostCreate
from app.services.beach import BeachService
from app.services.fishing_point import FishingPointService
from app.services.post import PostService


MYSQL_URL = os.getenv("TEST_MYSQL_URL")
pytestmark = pytest.mark.skipif(not MYSQL_URL, reason="TEST_MYSQL_URL não configurada")


def test_spatial_round_trip_and_archive_preserve_fishing_points() -> None:
    assert MYSQL_URL is not None
    engine = create_engine(MYSQL_URL, pool_pre_ping=True)

    with Session(engine, expire_on_commit=False) as session:
        session.execute(text("DELETE FROM pontos_pesca"))
        session.execute(text("DELETE FROM equipment_specifications"))
        session.execute(text("DELETE FROM posts"))
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

        point = FishingPointService(session).create(
            beach.id,
            FishingPointCreate(
                name="Canal teste",
                point_type=FishingPointType.CANAL_RETORNO,
                latitude=-22.93,
                longitude=-42.49,
                accessibility=AccessibilityLevel.MODERADA,
                risk_notes="Corrente forte na maré vazante.",
            ),
            actor=actor,
        )
        point_latitude, point_longitude = session.execute(
            text(
                "SELECT ST_Latitude(location), ST_Longitude(location) "
                "FROM pontos_pesca WHERE id = :point_id"
            ),
            {"point_id": point.id},
        ).one()
        assert float(point_latitude) == pytest.approx(-22.93)
        assert float(point_longitude) == pytest.approx(-42.49)

        post = PostService(session).create(
            PostCreate(
                title="Conjunto tubular 4,5 m para long cast",
                content="Ficha detalhada do conjunto para arremessos de alta distância na praia.",
                content_type=PostContentType.EQUIPAMENTO,
                status=PostStatus.PUBLICADO,
                equipment_specification=EquipmentSpecificationInput(
                    rod_length_m=4.5,
                    rod_construction="tubular",
                    reel_size=9000,
                    main_line_material="monofilamento",
                    main_line_diameter_mm=0.18,
                    shock_leader_type="cônico",
                ),
            ),
            actor=actor,
        )
        specification = session.execute(
            text(
                "SELECT rod_length_m, reel_size, main_line_diameter_mm "
                "FROM equipment_specifications WHERE post_id = :post_id"
            ),
            {"post_id": post.id},
        ).one()
        assert float(specification.rod_length_m) == pytest.approx(4.5)
        assert specification.reel_size == 9000
        assert float(specification.main_line_diameter_mm) == pytest.approx(0.18)

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
        session.execute(text("DELETE FROM equipment_specifications"))
        session.execute(text("DELETE FROM posts"))
        session.execute(text("DELETE FROM praias"))
        session.execute(text("DELETE FROM users"))
        session.commit()
