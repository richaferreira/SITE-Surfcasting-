from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text

from app.core.config import get_settings
from app.db import SessionLocal


@dataclass(frozen=True)
class BeachSeed:
    name: str
    slug: str
    city: str
    latitude: float
    longitude: float
    sea_bearing_deg: float
    beach_profile: str
    description: str


BEACHES = (
    BeachSeed("Praia de Itaúna", "praia-de-itauna", "Saquarema", -22.93598, -42.44065, 160.0, "INTERMEDIARIA", "Praia oceânica de Saquarema incluída no catálogo inicial da plataforma. A orientação operacional deve ser refinada com validação local."),
    BeachSeed("Praia da Vila", "praia-da-vila-saquarema", "Saquarema", -22.93451, -42.50155, 170.0, "INTERMEDIARIA", "Trecho urbano de Saquarema. Consulte mar, vento, sinalização e condições de acesso antes da pescaria."),
    BeachSeed("Praia de Jaconé", "praia-de-jacone", "Saquarema", -22.93734, -42.64155, 170.0, "INTERMEDIARIA", "Praia oceânica extensa no setor oeste de Saquarema. Spots e estruturas devem ser confirmados em campo."),
    BeachSeed("Praia de Barra Nova", "praia-de-barra-nova-saquarema", "Saquarema", -22.93300, -42.58500, 170.0, "INTERMEDIARIA", "Praia de Barra Nova, Saquarema. O catálogo publica apenas a referência geográfica; pontos de pesca exigem validação específica."),
    BeachSeed("Praia de Massambaba", "praia-de-massambaba", "Arraial do Cabo", -22.93667, -42.31499, 175.0, "INTERMEDIARIA", "Trecho oceânico associado à restinga de Massambaba. Respeite unidades de conservação, acessos autorizados e regras locais."),
    BeachSeed("Praia Grande", "praia-grande-arraial-do-cabo", "Arraial do Cabo", -22.96644, -42.02239, 235.0, "TOMBO", "Praia oceânica de Arraial do Cabo. Condições podem mudar rapidamente; use a telemetria e observe sinalização e correntes."),
    BeachSeed("Praia do Foguete", "praia-do-foguete", "Cabo Frio", -22.91781, -42.03436, 135.0, "INTERMEDIARIA", "Praia oceânica entre Cabo Frio e Arraial do Cabo. Pontos específicos são cadastrados somente após validação."),
    BeachSeed("Praia do Peró", "praia-do-pero", "Cabo Frio", -22.861328, -41.985153, 105.0, "INTERMEDIARIA", "Praia do Peró, Cabo Frio. A referência geográfica inicial usa ponto público de monitoramento costeiro."),
)


UPSERT = text(
    """
    INSERT INTO praias (
        name, slug, city, state, description, latitude, longitude, location,
        sea_bearing_deg, beach_profile, accessibility_summary, is_published,
        created_by, updated_by
    ) VALUES (
        :name, :slug, :city, 'RJ', :description, :latitude, :longitude,
        ST_SRID(POINT(:longitude, :latitude), 4326),
        :sea_bearing_deg, :beach_profile,
        'Consulte condições locais, sinalização, regras ambientais e segurança do acesso antes da pescaria.',
        TRUE, :admin_id, :admin_id
    )
    ON DUPLICATE KEY UPDATE
        name = VALUES(name), city = VALUES(city), state = VALUES(state),
        description = VALUES(description), latitude = VALUES(latitude), longitude = VALUES(longitude),
        location = VALUES(location), sea_bearing_deg = VALUES(sea_bearing_deg),
        beach_profile = VALUES(beach_profile), accessibility_summary = VALUES(accessibility_summary),
        is_published = TRUE, updated_by = VALUES(updated_by)
    """
)


def main() -> None:
    settings = get_settings()
    with SessionLocal() as db:
        admin_id = db.execute(
            text("SELECT id FROM users WHERE email = :email LIMIT 1"),
            {"email": settings.admin_email.lower()},
        ).scalar_one_or_none()
        if admin_id is None:
            raise SystemExit("Crie o administrador com scripts/create_admin.py antes de executar o seed.")

        for beach in BEACHES:
            db.execute(UPSERT, {**beach.__dict__, "admin_id": admin_id})
        db.commit()

        existing_slugs = set(db.execute(text("SELECT slug FROM praias WHERE is_published = TRUE")).scalars().all())
        expected_slugs = {beach.slug for beach in BEACHES}
        missing = sorted(expected_slugs - existing_slugs)
        if missing:
            raise SystemExit("Seed regional incompleto: " + ", ".join(missing))
        print(f"Catálogo regional atualizado: {len(expected_slugs)}/{len(BEACHES)} praias.")


if __name__ == "__main__":
    main()
