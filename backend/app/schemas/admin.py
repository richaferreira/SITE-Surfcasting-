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


class AdminPostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=4, max_length=200)
    slug: str | None = Field(default=None, min_length=3, max_length=220, pattern=r"^[a-z0-9-]+$")
    excerpt: str | None = Field(default=None, max_length=500)
    content: str | None = Field(default=None, min_length=20)
    content_type: str | None = Field(default=None, pattern=r"^(ARTIGO|TUTORIAL|VIDEO|EQUIPAMENTO)$")
    featured_image_url: str | None = Field(default=None, max_length=500)
    video_url: str | None = Field(default=None, max_length=500)
