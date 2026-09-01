from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models.enums import RoleCode
from app.models.user import User


class UserRegistration(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    username: str = Field(min_length=3, max_length=60, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name", "username", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.lower()

    @model_validator(mode="after")
    def validate_password_strength(self) -> "UserRegistration":
        if not any(character.isalpha() for character in self.password):
            raise ValueError("A senha deve possuir pelo menos uma letra.")
        if not any(character.isdigit() for character in self.password):
            raise ValueError("A senha deve possuir pelo menos um número.")
        return self


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    email: EmailStr
    role: RoleCode
    is_active: bool
    created_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            name=user.name,
            username=user.username,
            email=user.email,
            role=RoleCode(user.role.code),
            is_active=user.is_active,
            created_at=user.created_at,
        )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class AdminUserUpdate(BaseModel):
    role: RoleCode | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def reject_empty(self) -> "AdminUserUpdate":
        if not self.model_fields_set:
            raise ValueError("Informe papel ou status para atualização.")
        return self


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    offset: int
    limit: int
