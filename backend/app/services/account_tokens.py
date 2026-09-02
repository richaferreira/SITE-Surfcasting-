from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import token_digest


VERIFY_EMAIL = "VERIFY_EMAIL"
RESET_PASSWORD = "RESET_PASSWORD"


def create_account_token(db: Session, user_id: int, purpose: str, ttl: timedelta) -> str:
    raw_token = token_urlsafe(48)
    digest = token_digest(raw_token)
    expires_at = (datetime.now(UTC) + ttl).replace(tzinfo=None)

    db.execute(
        text(
            """
            DELETE FROM account_tokens
            WHERE user_id = :user_id AND purpose = :purpose AND used_at IS NULL
            """
        ),
        {"user_id": user_id, "purpose": purpose},
    )
    db.execute(
        text(
            """
            INSERT INTO account_tokens (user_id, token_hash, purpose, expires_at)
            VALUES (:user_id, :token_hash, :purpose, :expires_at)
            """
        ),
        {"user_id": user_id, "token_hash": digest, "purpose": purpose, "expires_at": expires_at},
    )
    return raw_token


def create_email_verification_token(db: Session, user_id: int) -> str:
    return create_account_token(db, user_id, VERIFY_EMAIL, timedelta(hours=24))


def create_password_reset_token(db: Session, user_id: int) -> str:
    return create_account_token(db, user_id, RESET_PASSWORD, timedelta(minutes=30))


def consume_account_token(db: Session, raw_token: str, purpose: str) -> int | None:
    digest = token_digest(raw_token)
    row = db.execute(
        text(
            """
            SELECT id, user_id
            FROM account_tokens
            WHERE token_hash = :token_hash
              AND purpose = :purpose
              AND used_at IS NULL
              AND expires_at > UTC_TIMESTAMP()
            LIMIT 1
            FOR UPDATE
            """
        ),
        {"token_hash": digest, "purpose": purpose},
    ).mappings().first()
    if not row:
        return None

    db.execute(
        text("UPDATE account_tokens SET used_at = UTC_TIMESTAMP() WHERE id = :id"),
        {"id": row["id"]},
    )
    return int(row["user_id"])
