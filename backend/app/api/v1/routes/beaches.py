from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.db import get_db
from app.schemas.beach import BeachCreate, BeachDetail, BeachSummary, FishingPointCreate, FishingPointResponse

router = APIRouter(prefix="/beaches", tags=["Praias"])

BEACH_FIELDS = """
    p.id, p.name, p.slug, p.city, p.state, p.description,
    CAST(p.latitude AS DOUBLE) AS latitude,
    CAST(p.longitude AS DOUBLE) AS longitude,
    CAST(p.sea_bearing_deg AS DOUBLE) AS sea_bearing_deg,
    p.beach_profile, p.accessibility_summary
"""

POINT_FIELDS = """
    id, praia_id, name, slug, point_type, description,
    CAST(latitude AS DOUBLE) AS latitude,
    CAST(longitude AS DOUBLE) AS longitude,
    accessibility, access_notes, risk_notes
"""


@router.get("", response_model=list[BeachSummary])
def list_beaches(
    city: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
) -> list[BeachSummary]:
    where = "WHERE p.is_published = TRUE"
    params: dict[str, object] = {}
    if city:
        where += " AND LOWER(p.city) = LOWER(:city)"
        params["city"] = city

    rows = db.execute(
        text(f"SELECT {BEACH_FIELDS} FROM praias p {where} ORDER BY p.city, p.name"),
        params,
    ).mappings().all()
    return [BeachSummary.model_validate(dict(row)) for row in rows]


@router.get("/{slug}", response_model=BeachDetail)
def get_beach(slug: str, db: Session = Depends(get_db)) -> BeachDetail:
    row = db.execute(
        text(f"SELECT {BEACH_FIELDS} FROM praias p WHERE p.slug = :slug AND p.is_published = TRUE LIMIT 1"),
        {"slug": slug},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Praia não encontrada.")

    points = db.execute(
        text(f"SELECT {POINT_FIELDS} FROM pontos_pesca WHERE praia_id = :praia_id AND is_active = TRUE ORDER BY name"),
        {"praia_id": row["id"]},
    ).mappings().all()
    payload = dict(row)
    payload["points"] = [FishingPointResponse.model_validate(dict(point)) for point in points]
    return BeachDetail.model_validate(payload)


@router.post("", response_model=BeachSummary, status_code=status.HTTP_201_CREATED)
def create_beach(
    payload: BeachCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "AUTHOR")),
) -> BeachSummary:
    try:
        result = db.execute(
            text(
                """
                INSERT INTO praias (
                    name, slug, city, state, description, latitude, longitude, location,
                    sea_bearing_deg, beach_profile, accessibility_summary, is_published,
                    created_by, updated_by
                ) VALUES (
                    :name, :slug, :city, :state, :description, :latitude, :longitude,
                    ST_SRID(POINT(:longitude, :latitude), 4326), :sea_bearing_deg,
                    :beach_profile, :accessibility_summary, :is_published, :user_id, :user_id
                )
                """
            ),
            {**payload.model_dump(), "user_id": current_user["id"]},
        )
        beach_id = result.lastrowid
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe uma praia com esse slug.") from exc

    row = db.execute(
        text(f"SELECT {BEACH_FIELDS} FROM praias p WHERE p.id = :id"),
        {"id": beach_id},
    ).mappings().one()
    return BeachSummary.model_validate(dict(row))


@router.post("/{slug}/points", response_model=FishingPointResponse, status_code=status.HTTP_201_CREATED)
def create_fishing_point(
    slug: str,
    payload: FishingPointCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "AUTHOR")),
) -> FishingPointResponse:
    beach_id = db.execute(text("SELECT id FROM praias WHERE slug = :slug LIMIT 1"), {"slug": slug}).scalar_one_or_none()
    if beach_id is None:
        raise HTTPException(status_code=404, detail="Praia não encontrada.")

    try:
        result = db.execute(
            text(
                """
                INSERT INTO pontos_pesca (
                    praia_id, name, slug, point_type, description, latitude, longitude,
                    location, accessibility, access_notes, risk_notes, created_by
                ) VALUES (
                    :praia_id, :name, :slug, :point_type, :description, :latitude, :longitude,
                    ST_SRID(POINT(:longitude, :latitude), 4326), :accessibility,
                    :access_notes, :risk_notes, :created_by
                )
                """
            ),
            {**payload.model_dump(), "praia_id": beach_id, "created_by": current_user["id"]},
        )
        point_id = result.lastrowid
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe um ponto com esse slug nesta praia.") from exc

    row = db.execute(
        text(f"SELECT {POINT_FIELDS} FROM pontos_pesca WHERE id = :id"),
        {"id": point_id},
    ).mappings().one()
    return FishingPointResponse.model_validate(dict(row))


@router.post("/{slug}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def favorite_beach(
    slug: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> None:
    beach_id = db.execute(text("SELECT id FROM praias WHERE slug = :slug AND is_published = TRUE"), {"slug": slug}).scalar_one_or_none()
    if beach_id is None:
        raise HTTPException(status_code=404, detail="Praia não encontrada.")
    db.execute(
        text("INSERT IGNORE INTO praia_favorites (user_id, praia_id) VALUES (:user_id, :praia_id)"),
        {"user_id": current_user["id"], "praia_id": beach_id},
    )
    db.commit()


@router.delete("/{slug}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def unfavorite_beach(
    slug: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> None:
    db.execute(
        text(
            """
            DELETE pf FROM praia_favorites pf
            JOIN praias p ON p.id = pf.praia_id
            WHERE pf.user_id = :user_id AND p.slug = :slug
            """
        ),
        {"user_id": current_user["id"], "slug": slug},
    )
    db.commit()
