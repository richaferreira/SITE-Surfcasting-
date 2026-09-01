from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.db import get_db
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


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
        user_id = result.lastrowid
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="E-mail ou nome de usuário já cadastrado.") from exc

    row = db.execute(
        text(
            """
            SELECT u.id, u.name, u.username, u.email, u.avatar_url, u.bio, r.code AS role
            FROM users u JOIN roles r ON r.id = u.role_id
            WHERE u.id = :user_id
            """
        ),
        {"user_id": user_id},
    ).mappings().one()
    user = _public_user(dict(row))
    token = create_access_token(str(user.id), user.role)
    return AuthResponse(access_token=token, user=user)


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
    db.commit()
    user = _public_user(dict(row))
    token = create_access_token(str(user.id), user.role)
    return AuthResponse(access_token=token, user=user)


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    return _public_user(current_user)
