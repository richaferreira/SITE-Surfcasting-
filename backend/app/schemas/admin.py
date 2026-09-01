from pydantic import BaseModel, Field


class AdminDashboard(BaseModel):
    users: int
    active_users: int
    beaches: int
    published_beaches: int
    posts: int
    published_posts: int
    catches: int
    comments: int


class AdminUser(BaseModel):
    id: int
    name: str
    username: str
    email: str
    role: str
    is_active: bool


class ChangeRoleRequest(BaseModel):
    role: str = Field(pattern=r"^(ADMIN|AUTHOR|USER)$")


class ChangeActiveRequest(BaseModel):
    is_active: bool


class ChangePostStatusRequest(BaseModel):
    status: str = Field(pattern=r"^(RASCUNHO|EM_REVISAO|PUBLICADO|ARQUIVADO)$")
