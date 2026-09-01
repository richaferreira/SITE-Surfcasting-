from pydantic import BaseModel, Field


class SpeciesRecommendationResponse(BaseModel):
    species: str
    scientific_name: str | None
    relevance: float = Field(ge=0)


class RecommendationListResponse(BaseModel):
    beach_slug: str
    wind_direction: str
    items: list[SpeciesRecommendationResponse]

