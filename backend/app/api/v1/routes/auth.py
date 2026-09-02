from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies.rate_limit import enforce_auth_rate_limit
from app.core.config import get_settings
from app.core.security import (
    clear_auth_cookies,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user,
    hash_password,
    set_auth_cookies,
    token_digest,
    verify_password,
)
from app.db import get_db
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    ProfileUpdate,
    RefreshRequest,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    UserResponse,
    VerifyEmailRequest,
)
from app.services.account_tokens import (
    RESET_PASSWORD,
    VERIFY_EMAIL,
    consume_account_token,
    create_email_verification_token,
    create_password_reset_token,
)
from app.services.email import send_transactional_email

router = APIRouter(prefix="/auth", tags=["Autenticação"])
settings = get_settings()

USER_SELECT = """
    SELECT u.id, u.name, u.username, u.email, u.avatar_url, u.bio, u.is_active,
           u.email_verified_at, r.code AS role
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
        email_verified=bool(row.get("email_verified_at")),
    )


def _issue_session(
    db: Session,
    user: UserResponse,
    response: Response,
    old_refresh_hash: str | None = None,
) -> AuthResponse:
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

    set_auth_cookies(response, access_token, refresh_token)
    return AuthResponse(user=user)


def _send_verification(email: str, token: str) -> None:
    url = f"{settings.frontend_url.rstrip('/')}/verificar-email?token={token}"
    send_transactional_email(
        email,
        "Confirme seu e-mail — Surfcasting Região dos Lagos",
        "Confirme seu cadastro acessando o link abaixo. O link expira em 24 horas.\n\n" + url,
    )


def _send_password_reset(email: str, token: str) -> None:
    url = f"{settings.frontend_url.rstrip('/')}/redefinir-senha?token={token}"
    send_transactional_email(
        email,
        "Redefinição de senha — Surfcasting Região dos Lagos",
        "Foi solicitada uma redefinição de senha. O link expira em 30 minutos.\n\n" + url,
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_auth_rate_limit)],
)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    role_id = db.execute(text("SELECT id FROM roles WHERE code = 'USER' LIMIT 1")).scalar_one_or_none()
    if role_id is None:
        raise HTTPException(status_code=500, detail="Perfil USER não foi inicializado no banco.")

    try:
        result = db.execute(
            text(
                """
                INSERT INTO users (
                    role_id, name, username, email, password_hash,
                    accepted_terms_at, accepted_privacy_at
                )
                VALUES (
                    :role_id, :name, :username, :email, :password_hash,
                    UTC_TIMESTAMP(), UTC_TIMESTAMP()
                )
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
        verification_token = create_email_verification_token(db, user_id)
        row = db.execute(text(USER_SELECT + " WHERE u.id = :user_id"), {"user_id": user_id}).mappings().one()
        user = _public_user(dict(row))
        auth_response = _issue_session(db, user, response)
        db.commit()
        try:
            _send_verification(user.email, verification_token)
        except Exception as exc:
            print(f"[EMAIL ERROR] verification user={user.id}: {exc}")
        return auth_response
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="E-mail ou nome de usuário já cadastrado.") from exc


@router.post("/login", response_model=AuthResponse, dependencies=[Depends(enforce_auth_rate_limit)])
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    identifier = payload.login.strip().lower()
    row = db.execute(
        text(
            """
            SELECT u.id, u.name, u.username, u.email, u.password_hash, u.avatar_url, u.bio,
                   u.is_active, u.email_verified_at, r.code AS role
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
    auth_response = _issue_session(db, user, response)
    db.commit()
    return auth_response


@router.post("/refresh", response_model=AuthResponse)
def refresh(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
    db: Session = Depends(get_db),
) -> AuthResponse:
    raw_refresh = (payload.refresh_token if payload else None) or request.cookies.get(settings.refresh_cookie_name)
    if not raw_refresh:
        raise HTTPException(status_code=401, detail="Refresh token ausente.")

    decoded = decode_refresh_token(raw_refresh)
    refresh_hash = token_digest(raw_refresh)
    row = db.execute(
        text(
            """
            SELECT u.id, u.name, u.username, u.email, u.avatar_url, u.bio, u.is_active,
                   u.email_verified_at, r.code AS role, rt.user_id AS token_user_id
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
        clear_auth_cookies(response)
        raise HTTPException(status_code=401, detail="Refresh token inválido, revogado ou expirado.")

    user = _public_user(dict(row))
    auth_response = _issue_session(db, user, response, old_refresh_hash=refresh_hash)
    db.commit()
    return auth_response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    payload: LogoutRequest | None = None,
    db: Session = Depends(get_db),
) -> None:
    raw_refresh = (payload.refresh_token if payload else None) or request.cookies.get(settings.refresh_cookie_name)
    if raw_refresh:
        db.execute(
            text(
                """
                UPDATE refresh_tokens
                SET revoked_at = COALESCE(revoked_at, CURRENT_TIMESTAMP)
                WHERE token_hash = :token_hash
                """
            ),
            {"token_hash": token_digest(raw_refresh)},
        )
        db.commit()
    clear_auth_cookies(response)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    dependencies=[Depends(enforce_auth_rate_limit)],
)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    email = str(payload.email).lower()
    row = db.execute(
        text("SELECT id, email, is_active FROM users WHERE LOWER(email) = :email LIMIT 1"),
        {"email": email},
    ).mappings().first()
    if row and row["is_active"]:
        token = create_password_reset_token(db, int(row["id"]))
        db.commit()
        try:
            _send_password_reset(str(row["email"]), token)
        except Exception as exc:
            print(f"[EMAIL ERROR] password-reset user={row['id']}: {exc}")
    return MessageResponse(message="Se o e-mail estiver cadastrado, enviaremos as instruções de redefinição.")


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    dependencies=[Depends(enforce_auth_rate_limit)],
)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    user_id = consume_account_token(db, payload.token, RESET_PASSWORD)
    if user_id is None:
        db.rollback()
        raise HTTPException(status_code=400, detail="Token de redefinição inválido ou expirado.")

    db.execute(
        text("UPDATE users SET password_hash = :password_hash WHERE id = :user_id"),
        {"password_hash": hash_password(payload.new_password), "user_id": user_id},
    )
    db.execute(
        text(
            """
            UPDATE refresh_tokens SET revoked_at = COALESCE(revoked_at, UTC_TIMESTAMP())
            WHERE user_id = :user_id
            """
        ),
        {"user_id": user_id},
    )
    db.commit()
    return MessageResponse(message="Senha redefinida. Entre novamente com a nova senha.")


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> MessageResponse:
    user_id = consume_account_token(db, payload.token, VERIFY_EMAIL)
    if user_id is None:
        db.rollback()
        raise HTTPException(status_code=400, detail="Token de verificação inválido ou expirado.")
    db.execute(
        text("UPDATE users SET email_verified_at = COALESCE(email_verified_at, UTC_TIMESTAMP()) WHERE id = :id"),
        {"id": user_id},
    )
    db.commit()
    return MessageResponse(message="E-mail verificado com sucesso.")


@router.post(
    "/resend-verification",
    response_model=MessageResponse,
    dependencies=[Depends(enforce_auth_rate_limit)],
)
def resend_verification(payload: ResendVerificationRequest, db: Session = Depends(get_db)) -> MessageResponse:
    row = db.execute(
        text(
            """
            SELECT id, email, is_active, email_verified_at
            FROM users WHERE LOWER(email) = :email LIMIT 1
            """
        ),
        {"email": str(payload.email).lower()},
    ).mappings().first()
    if row and row["is_active"] and not row["email_verified_at"]:
        token = create_email_verification_token(db, int(row["id"]))
        db.commit()
        try:
            _send_verification(str(row["email"]), token)
        except Exception as exc:
            print(f"[EMAIL ERROR] resend-verification user={row['id']}: {exc}")
    return MessageResponse(message="Se a conta precisar de confirmação, um novo link será enviado.")


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
