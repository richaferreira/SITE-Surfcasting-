from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user,
    hash_password,
    token_digest,
    verify_password,
)
from app.db import get_db
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    ProfileUpdate,
    RefreshRequest,
    RegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])

USER_SELECT = """
    SELECT u.id, u.name, u.username, u.email, u.avatar_url, u.bio, u.is_active,
           r.code AS role
    FROM users u
    JOIN roles r ON r.id = u.role_id
"""


def _public_user(row: dict) -> UserResponse:
    return UserResponse(
        id=row["id"],
        name=row["name"],
        username=row["username"],
        email=row["email"],
        role=row["role"],
        avatar_url=row.get("avatar_url"),
        bio=row.get("bio"),
    )


def _issue_tokens(db: Session, user: UserResponse, old_refresh_hash: str | None = None) -> AuthResponse:
    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id))
    refresh_payload = decode_refresh_token(refresh_token)
    expires_at = datetime.fromtimestamp(int(refresh_payload["exp"]), UTC).replace(tzinfo=None)
    refresh_hash = token_digest(refresh_token)

    db.execute(
        text(
            """
            INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
            VALUES (:user_id, :token_hash, :expires_at)
            """
        ),
        {"user_id": user.id, "token_hash": refresh_hash, "expires_at": expires_at},
    )

    if old_refresh_hash:
        db.execute(
            text(
                """
                UPDATE refresh_tokens
                SET revoked_at = CURRENT_TIMESTAMP, replaced_by_hash = :replacement
                WHERE token_hash = :old_hash AND revoked_at IS NULL
                """
            ),
            {"replacement": refresh_hash, "old_hash": old_refresh_hash},
        )

    return AuthResponse(access_token=access_token, refresh_token=refresh_token, user=user)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    role_id = db.execute(text("SELECT id FROM roles WHERE code = 'USER' LIMIT 1")).scalar_one_or_none()
    if role_id is None:
        raise HTTPException(status_code=500, detail="Perfil USER não foi inicializado no banco.")

    try:
        result = db.execute(
            text(
                """
                INSERT INTO users (role_id, name, username, email, password_hash)
                VALUES (:role_id, :name, :username, :email, :password_hash)
                """
            ),
            {
                "role_id": role_id,
                "name": payload.name,
                "username": payload.username.lower(),
                "email": str(payload.email).lower(),
                "password_hash": hash_password(payload.password),
            },
        )
        user_id = int(result.lastrowid)
        row = db.execute(text(USER_SELECT + " WHERE u.id = :user_id"), {"user_id": user_id}).mappings().one()
        user = _public_user(dict(row))
        response = _issue_tokens(db, user)
        db.commit()
        return response
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="E-mail ou nome de usuário já cadastrado.") from exc


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    identifier = payload.login.strip().lower()
    row = db.execute(
        text(
            """
            SELECT u.id, u.name, u.username, u.email, u.password_hash, u.avatar_url, u.bio,
                   u.is_active, r.code AS role
            FROM users u JOIN roles r ON r.id = u.role_id
            WHERE LOWER(u.email) = :identifier OR LOWER(u.username) = :identifier
            LIMIT 1
            """
        ),
        {"identifier": identifier},
    ).mappings().first()

    if not row or not row["is_active"] or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    db.execute(text("UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = :id"), {"id": row["id"]})
    user = _public_user(dict(row))
    response = _issue_tokens(db, user)
    db.commit()
    return response


@router.post("/refresh", response_model=AuthResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> AuthResponse:
    decoded = decode_refresh_token(payload.refresh_token)
    refresh_hash = token_digest(payload.refresh_token)
    row = db.execute(
        text(
            """
            SELECT u.id, u.name, u.username, u.email, u.avatar_url, u.bio, u.is_active,
                   r.code AS role, rt.user_id AS token_user_id
            FROM refresh_tokens rt
            JOIN users u ON u.id = rt.user_id
            JOIN roles r ON r.id = u.role_id
            WHERE rt.token_hash = :token_hash
              AND rt.revoked_at IS NULL
              AND rt.expires_at > UTC_TIMESTAMP()
            LIMIT 1
            """
        ),
        {"token_hash": refresh_hash},
    ).mappings().first()

    if not row or not row["is_active"] or str(row["token_user_id"]) != str(decoded.get("sub")):
        raise HTTPException(status_code=401, detail="Refresh token inválido, revogado ou expirado.")

    user = _public_user(dict(row))
    response = _issue_tokens(db, user, old_refresh_hash=refresh_hash)
    db.commit()
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)) -> None:
    db.execute(
        text(
            """
            UPDATE refresh_tokens
            SET revoked_at = COALESCE(revoked_at, CURRENT_TIMESTAMP)
            WHERE token_hash = :token_hash
            """
        ),
        {"token_hash": token_digest(payload.refresh_token)},
    )
    db.commit()


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    return _public_user(current_user)


@router.patch("/me", response_model=UserResponse)
def update_me(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return _public_user(current_user)

    allowed = {"name", "bio", "avatar_url"}
    assignments = [f"{field} = :{field}" for field in updates if field in allowed]
    if not assignments:
        return _public_user(current_user)

    db.execute(
        text(f"UPDATE users SET {', '.join(assignments)} WHERE id = :user_id"),
        {**updates, "user_id": current_user["id"]},
    )
    db.commit()
    row = db.execute(text(USER_SELECT + " WHERE u.id = :user_id"), {"user_id": current_user["id"]}).mappings().one()
    return _public_user(dict(row))
