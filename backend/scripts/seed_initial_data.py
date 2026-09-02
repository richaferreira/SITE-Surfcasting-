from sqlalchemy import text

from app.core.config import get_settings
from app.db import SessionLocal


def main() -> None:
    settings = get_settings()
    with SessionLocal() as db:
        admin_id = db.execute(
            text("SELECT id FROM users WHERE email = :email LIMIT 1"),
            {"email": settings.admin_email.lower()},
        ).scalar_one_or_none()
        if admin_id is None:
            raise SystemExit("Crie o administrador com scripts/create_admin.py antes de executar o seed.")

        exists = db.execute(text("SELECT id FROM praias WHERE slug = 'praia-de-itauna' LIMIT 1")).scalar_one_or_none()
        if exists:
            print("Praia de Itaúna já cadastrada.")
            return

        db.execute(
            text(
                """
                INSERT INTO praias (
                    name, slug, city, state, description, latitude, longitude, location,
                    sea_bearing_deg, beach_profile, accessibility_summary, is_published,
                    created_by, updated_by
                ) VALUES (
                    'Praia de Itaúna', 'praia-de-itauna', 'Saquarema', 'RJ',
                    'Praia de referência inicial da plataforma Surfcasting Região dos Lagos.',
                    -22.935000, -42.483000,
                    ST_SRID(POINT(-42.483000, -22.935000), 4326),
                    160.00, 'INTERMEDIARIA',
                    'Consulte as condições locais e a sinalização de acesso antes da pescaria.',
                    TRUE, :admin_id, :admin_id
                )
                """
            ),
            {"admin_id": admin_id},
        )
        db.commit()
        print("Praia de Itaúna cadastrada.")


if __name__ == "__main__":
    main()
