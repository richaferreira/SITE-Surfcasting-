from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.config import Settings, get_settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse, UserRegistration, UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserRegistration,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    user = AuthService(db).register(payload)
    return UserResponse.from_user(user)


@router.post("/token", response_model=TokenResponse)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    user = AuthService(db).authenticate(form.username, form.password)
    access_token, expires_in = create_access_token(user.id, settings)
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserResponse.from_user(user),
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse.from_user(current_user)
