from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.db import get_db
from app.schemas.beach import (
    BeachCreate,
    BeachDetail,
    BeachSummary,
    BeachUpdate,
    FishingPointCreate,
    FishingPointResponse,
    FishingPointUpdate,
)

router = APIRouter(prefix="/beaches", tags=["Praias"])

BEACH_FIELDS = """
    p.id, p.name, p.slug, p.city, p.state, p.description,
    CAST(p.latitude AS DOUBLE) AS latitude,
    CAST(p.longitude AS DOUBLE) AS longitude,
    CAST(p.sea_bearing_deg AS DOUBLE) AS sea_bearing_deg,
    p.beach_profile, p.accessibility_summary, p.is_published
"""

POINT_FIELDS = """
    id, praia_id, name, slug, point_type, description,
    CAST(latitude AS DOUBLE) AS latitude,
    CAST(longitude AS DOUBLE) AS longitude,
    accessibility, access_notes, risk_notes, is_active
"""


def _assert_beach_manager(db: Session, slug: str, current_user: dict) -> dict:
    row = db.execute(
        text(
            """
            SELECT id, created_by, name, slug, city, state, description,
                   CAST(latitude AS DOUBLE) AS latitude,
                   CAST(longitude AS DOUBLE) AS longitude,
                   CAST(sea_bearing_deg AS DOUBLE) AS sea_bearing_deg,
                   beach_profile, accessibility_summary, is_published
            FROM praias WHERE slug = :slug LIMIT 1
            """
        ),
        {"slug": slug},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Praia não encontrada.")
    if current_user["role"] != "ADMIN" and row["created_by"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Você só pode administrar praias criadas por você.")
    return dict(row)


def _point_for_management(db: Session, praia_id: int, point_id: int, current_user: dict) -> dict:
    row = db.execute(
        text(
            """
            SELECT id, praia_id, created_by, name, slug, point_type, description,
                   CAST(latitude AS DOUBLE) AS latitude,
                   CAST(longitude AS DOUBLE) AS longitude,
                   accessibility, access_notes, risk_notes, is_active
            FROM pontos_pesca
            WHERE id = :point_id AND praia_id = :praia_id
            LIMIT 1
            """
        ),
        {"point_id": point_id, "praia_id": praia_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Ponto de pesca não encontrado.")
    if current_user["role"] != "ADMIN" and row["created_by"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Você só pode administrar pontos criados por você.")
    return dict(row)


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


@router.get("/manage", response_model=list[BeachSummary])
def list_managed_beaches(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "AUTHOR")),
) -> list[BeachSummary]:
    if current_user["role"] == "ADMIN":
        rows = db.execute(text(f"SELECT {BEACH_FIELDS} FROM praias p ORDER BY p.city, p.name")).mappings().all()
    else:
        rows = db.execute(
            text(f"SELECT {BEACH_FIELDS} FROM praias p WHERE p.created_by = :user_id ORDER BY p.city, p.name"),
            {"user_id": current_user["id"]},
        ).mappings().all()
    return [BeachSummary.model_validate(dict(row)) for row in rows]


@router.get("/{slug}/manage", response_model=BeachDetail)
def get_managed_beach(
    slug: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "AUTHOR")),
) -> BeachDetail:
    managed = _assert_beach_manager(db, slug, current_user)
    points = db.execute(
        text(f"SELECT {POINT_FIELDS} FROM pontos_pesca WHERE praia_id = :praia_id ORDER BY name"),
        {"praia_id": managed["id"]},
    ).mappings().all()
    managed.pop("created_by", None)
    managed["points"] = [FishingPointResponse.model_validate(dict(point)) for point in points]
    return BeachDetail.model_validate(managed)


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
        beach_id = int(result.lastrowid)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe uma praia com esse slug.") from exc

    row = db.execute(text(f"SELECT {BEACH_FIELDS} FROM praias p WHERE p.id = :id"), {"id": beach_id}).mappings().one()
    return BeachSummary.model_validate(dict(row))


@router.patch("/{slug}", response_model=BeachSummary)
def update_beach(
    slug: str,
    payload: BeachUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "AUTHOR")),
) -> BeachSummary:
    existing = _assert_beach_manager(db, slug, current_user)
    updates = payload.model_dump(exclude_unset=True)
    required_fields = {"name", "slug", "city", "state", "latitude", "longitude", "sea_bearing_deg", "beach_profile", "is_published"}
    if any(field in updates and updates[field] is None for field in required_fields):
        raise HTTPException(status_code=422, detail="Campos obrigatórios da praia não podem ser nulos.")

    merged = {**existing, **updates}
    try:
        db.execute(
            text(
                """
                UPDATE praias SET
                    name = :name, slug = :new_slug, city = :city, state = :state,
                    description = :description, latitude = :latitude, longitude = :longitude,
                    location = ST_SRID(POINT(:longitude, :latitude), 4326),
                    sea_bearing_deg = :sea_bearing_deg, beach_profile = :beach_profile,
                    accessibility_summary = :accessibility_summary, is_published = :is_published,
                    updated_by = :updated_by
                WHERE id = :id
                """
            ),
            {
                "id": existing["id"],
                "name": merged["name"],
                "new_slug": merged["slug"],
                "city": merged["city"],
                "state": merged["state"],
                "description": merged.get("description"),
                "latitude": merged["latitude"],
                "longitude": merged["longitude"],
                "sea_bearing_deg": merged["sea_bearing_deg"],
                "beach_profile": merged["beach_profile"],
                "accessibility_summary": merged.get("accessibility_summary"),
                "is_published": merged["is_published"],
                "updated_by": current_user["id"],
            },
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="O novo slug já está em uso por outra praia.") from exc

    row = db.execute(text(f"SELECT {BEACH_FIELDS} FROM praias p WHERE p.id = :id"), {"id": existing["id"]}).mappings().one()
    return BeachSummary.model_validate(dict(row))


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_beach(
    slug: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "AUTHOR")),
) -> None:
    existing = _assert_beach_manager(db, slug, current_user)
    db.execute(text("DELETE FROM praias WHERE id = :id"), {"id": existing["id"]})
    db.commit()


@router.post("/{slug}/points", response_model=FishingPointResponse, status_code=status.HTTP_201_CREATED)
def create_fishing_point(
    slug: str,
    payload: FishingPointCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "AUTHOR")),
) -> FishingPointResponse:
    beach = _assert_beach_manager(db, slug, current_user)
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
            {**payload.model_dump(), "praia_id": beach["id"], "created_by": current_user["id"]},
        )
        point_id = int(result.lastrowid)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe um ponto com esse slug nesta praia.") from exc

    row = db.execute(text(f"SELECT {POINT_FIELDS} FROM pontos_pesca WHERE id = :id"), {"id": point_id}).mappings().one()
    return FishingPointResponse.model_validate(dict(row))


@router.patch("/{slug}/points/{point_id}", response_model=FishingPointResponse)
def update_fishing_point(
    slug: str,
    point_id: int,
    payload: FishingPointUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "AUTHOR")),
) -> FishingPointResponse:
    beach = _assert_beach_manager(db, slug, current_user)
    existing = _point_for_management(db, beach["id"], point_id, current_user)
    updates = payload.model_dump(exclude_unset=True)
    required_fields = {"name", "slug", "point_type", "latitude", "longitude", "accessibility", "is_active"}
    if any(field in updates and updates[field] is None for field in required_fields):
        raise HTTPException(status_code=422, detail="Campos obrigatórios do ponto não podem ser nulos.")
    merged = {**existing, **updates}

    try:
        db.execute(
            text(
                """
                UPDATE pontos_pesca SET
                    name = :name, slug = :new_slug, point_type = :point_type,
                    description = :description, latitude = :latitude, longitude = :longitude,
                    location = ST_SRID(POINT(:longitude, :latitude), 4326),
                    accessibility = :accessibility, access_notes = :access_notes,
                    risk_notes = :risk_notes, is_active = :is_active
                WHERE id = :id AND praia_id = :praia_id
                """
            ),
            {
                "id": point_id,
                "praia_id": beach["id"],
                "name": merged["name"],
                "new_slug": merged["slug"],
                "point_type": merged["point_type"],
                "description": merged.get("description"),
                "latitude": merged["latitude"],
                "longitude": merged["longitude"],
                "accessibility": merged["accessibility"],
                "access_notes": merged.get("access_notes"),
                "risk_notes": merged.get("risk_notes"),
                "is_active": merged["is_active"],
            },
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="O novo slug do ponto já está em uso nesta praia.") from exc

    row = db.execute(text(f"SELECT {POINT_FIELDS} FROM pontos_pesca WHERE id = :id"), {"id": point_id}).mappings().one()
    return FishingPointResponse.model_validate(dict(row))


@router.delete("/{slug}/points/{point_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fishing_point(
    slug: str,
    point_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "AUTHOR")),
) -> None:
    beach = _assert_beach_manager(db, slug, current_user)
    _point_for_management(db, beach["id"], point_id, current_user)
    db.execute(text("DELETE FROM pontos_pesca WHERE id = :id AND praia_id = :praia_id"), {"id": point_id, "praia_id": beach["id"]})
    db.commit()


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
