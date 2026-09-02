from sqlalchemy import text

from app.core.config import get_settings
from app.core.security import hash_password
from app.db import SessionLocal


def main() -> None:
    settings = get_settings()
    if settings.admin_password == "troque-esta-senha":
        raise SystemExit("Defina ADMIN_PASSWORD no arquivo .env antes de criar o administrador.")

    with SessionLocal() as db:
        role_id = db.execute(text("SELECT id FROM roles WHERE code = 'ADMIN' LIMIT 1")).scalar_one_or_none()
        if role_id is None:
            raise SystemExit("Role ADMIN não encontrada. Inicialize o schema MySQL primeiro.")

        existing = db.execute(
            text("SELECT id FROM users WHERE email = :email OR username = :username LIMIT 1"),
            {"email": settings.admin_email.lower(), "username": settings.admin_username.lower()},
        ).scalar_one_or_none()

        values = {
            "role_id": role_id,
            "name": settings.admin_name,
            "username": settings.admin_username.lower(),
            "email": settings.admin_email.lower(),
            "password_hash": hash_password(settings.admin_password),
        }

        if existing:
            db.execute(
                text(
                    """
                    UPDATE users
                    SET role_id = :role_id, name = :name, username = :username,
                        email = :email, password_hash = :password_hash, is_active = TRUE,
                        email_verified_at = COALESCE(email_verified_at, UTC_TIMESTAMP()),
                        accepted_terms_at = COALESCE(accepted_terms_at, UTC_TIMESTAMP()),
                        accepted_privacy_at = COALESCE(accepted_privacy_at, UTC_TIMESTAMP())
                    WHERE id = :id
                    """
                ),
                {**values, "id": existing},
            )
            message = f"Administrador atualizado: {settings.admin_email}"
        else:
            db.execute(
                text(
                    """
                    INSERT INTO users (
                        role_id, name, username, email, password_hash, is_active,
                        email_verified_at, accepted_terms_at, accepted_privacy_at
                    )
                    VALUES (
                        :role_id, :name, :username, :email, :password_hash, TRUE,
                        UTC_TIMESTAMP(), UTC_TIMESTAMP(), UTC_TIMESTAMP()
                    )
                    """
                ),
                values,
            )
            message = f"Administrador criado: {settings.admin_email}"

        db.commit()
        print(message)


if __name__ == "__main__":
    main()
