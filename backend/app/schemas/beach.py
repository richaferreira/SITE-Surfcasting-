from pydantic import BaseModel, Field


class FishingPointResponse(BaseModel):
    id: int
    praia_id: int
    name: str
    slug: str
    point_type: str
    description: str | None = None
    latitude: float
    longitude: float
    accessibility: str
    access_notes: str | None = None
    risk_notes: str | None = None
    is_active: bool


class BeachSummary(BaseModel):
    id: int
    name: str
    slug: str
    city: str
    state: str
    description: str | None = None
    latitude: float
    longitude: float
    sea_bearing_deg: float
    beach_profile: str
    accessibility_summary: str | None = None
    is_published: bool


class BeachDetail(BeachSummary):
    points: list[FishingPointResponse] = Field(default_factory=list)


class BeachCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    slug: str = Field(min_length=2, max_length=180, pattern=r"^[a-z0-9-]+$")
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(default="RJ", min_length=2, max_length=2)
    description: str | None = Field(default=None, max_length=10000)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    sea_bearing_deg: float = Field(ge=0, lt=360)
    beach_profile: str = Field(pattern=r"^(TOMBO|INTERMEDIARIA|RASA|ABRIGADA)$")
    accessibility_summary: str | None = Field(default=None, max_length=500)
    is_published: bool = True


class BeachUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    slug: str | None = Field(default=None, min_length=2, max_length=180, pattern=r"^[a-z0-9-]+$")
    city: str | None = Field(default=None, min_length=2, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    description: str | None = Field(default=None, max_length=10000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    sea_bearing_deg: float | None = Field(default=None, ge=0, lt=360)
    beach_profile: str | None = Field(default=None, pattern=r"^(TOMBO|INTERMEDIARIA|RASA|ABRIGADA)$")
    accessibility_summary: str | None = Field(default=None, max_length=500)
    is_published: bool | None = None


class FishingPointCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    slug: str = Field(min_length=2, max_length=180, pattern=r"^[a-z0-9-]+$")
    point_type: str = Field(pattern=r"^(BURACO|COROA_AREIA|CANAL_RETORNO|ESTRUTURA|OUTRO)$")
    description: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accessibility: str = Field(default="MODERADA", pattern=r"^(FACIL|MODERADA|DIFICIL|RESTRITA)$")
    access_notes: str | None = Field(default=None, max_length=500)
    risk_notes: str | None = Field(default=None, max_length=500)


class FishingPointUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    slug: str | None = Field(default=None, min_length=2, max_length=180, pattern=r"^[a-z0-9-]+$")
    point_type: str | None = Field(default=None, pattern=r"^(BURACO|COROA_AREIA|CANAL_RETORNO|ESTRUTURA|OUTRO)$")
    description: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    accessibility: str | None = Field(default=None, pattern=r"^(FACIL|MODERADA|DIFICIL|RESTRITA)$")
    access_notes: str | None = Field(default=None, max_length=500)
    risk_notes: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None
