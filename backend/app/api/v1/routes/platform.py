from datetime import UTC, datetime, timedelta
from io import BytesIO
import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_verified_user
from app.api.dependencies.rate_limit import enforce_community_rate_limit, enforce_public_api_rate_limit
from app.core.config import get_settings
from app.core.security import decode_access_token, get_current_user, require_roles
from app.db import get_db
from app.schemas.launch import (
    AnalyticsEventCreate,
    AnalyticsSummary,
    MediaAssetResponse,
    NotificationResponse,
    ReportCreate,
    ReportResponse,
    ReportStatusUpdate,
)

router = APIRouter(tags=["Plataforma"])
settings = get_settings()


@router.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(
    limit: int = Query(default=40, ge=1, le=100),
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> list[NotificationResponse]:
    condition = "AND read_at IS NULL" if unread_only else ""
    rows = db.execute(
        text(
            f"""
            SELECT id, notification_type, title, message, action_url, read_at, created_at
            FROM notifications
            WHERE user_id = :user_id {condition}
            ORDER BY created_at DESC
            LIMIT :limit
            """
        ),
        {"user_id": current_user["id"], "limit": limit},
    ).mappings().all()
    return [NotificationResponse.model_validate(dict(row)) for row in rows]


@router.post("/notifications/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> None:
    db.execute(
        text(
            """
            UPDATE notifications SET read_at = COALESCE(read_at, UTC_TIMESTAMP())
            WHERE id = :id AND user_id = :user_id
            """
        ),
        {"id": notification_id, "user_id": current_user["id"]},
    )
    db.commit()


@router.post("/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> None:
    db.execute(
        text("UPDATE notifications SET read_at = UTC_TIMESTAMP() WHERE user_id = :user_id AND read_at IS NULL"),
        {"user_id": current_user["id"]},
    )
    db.commit()


@router.post(
    "/reports",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_community_rate_limit)],
)
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_verified_user),
) -> ReportResponse:
    if payload.post_id is not None:
        exists = db.execute(text("SELECT id FROM posts WHERE id = :id"), {"id": payload.post_id}).scalar_one_or_none()
    else:
        exists = db.execute(text("SELECT id FROM post_comments WHERE id = :id"), {"id": payload.comment_id}).scalar_one_or_none()
    if exists is None:
        raise HTTPException(status_code=404, detail="Conteúdo denunciado não foi encontrado.")

    result = db.execute(
        text(
            """
            INSERT INTO community_reports (reporter_id, post_id, comment_id, reason, details)
            VALUES (:reporter_id, :post_id, :comment_id, :reason, :details)
            """
        ),
        {**payload.model_dump(), "reporter_id": current_user["id"]},
    )
    report_id = int(result.lastrowid)
    db.commit()
    row = db.execute(text("SELECT * FROM community_reports WHERE id = :id"), {"id": report_id}).mappings().one()
    return ReportResponse.model_validate(dict(row))


@router.get("/admin/reports", response_model=list[ReportResponse])
def admin_list_reports(
    report_status: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("ADMIN")),
) -> list[ReportResponse]:
    where = "WHERE status = :status" if report_status else ""
    params: dict[str, object] = {"limit": limit}
    if report_status:
        params["status"] = report_status
    rows = db.execute(
        text(f"SELECT * FROM community_reports {where} ORDER BY created_at DESC LIMIT :limit"),
        params,
    ).mappings().all()
    return [ReportResponse.model_validate(dict(row)) for row in rows]


@router.patch("/admin/reports/{report_id}", response_model=ReportResponse)
def admin_update_report(
    report_id: int,
    payload: ReportStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN")),
) -> ReportResponse:
    result = db.execute(
        text(
            """
            UPDATE community_reports
            SET status = :status, reviewed_by = :reviewed_by, reviewed_at = UTC_TIMESTAMP()
            WHERE id = :id
            """
        ),
        {"status": payload.status, "reviewed_by": current_user["id"], "id": report_id},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Denúncia não encontrada.")
    db.commit()
    row = db.execute(text("SELECT * FROM community_reports WHERE id = :id"), {"id": report_id}).mappings().one()
    return ReportResponse.model_validate(dict(row))


@router.post(
    "/analytics/events",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(enforce_public_api_rate_limit)],
)
def create_analytics_event(
    payload: AnalyticsEventCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    metadata_json = json.dumps(payload.metadata, ensure_ascii=False) if payload.metadata is not None else None
    if metadata_json and len(metadata_json) > 4000:
        raise HTTPException(status_code=422, detail="Metadados de analytics excedem o limite permitido.")

    user_id: int | None = None
    access_token = request.cookies.get(settings.access_cookie_name)
    if access_token:
        try:
            decoded = decode_access_token(access_token)
            user_id = int(decoded["sub"])
        except (HTTPException, KeyError, TypeError, ValueError):
            user_id = None

    db.execute(
        text(
            """
            INSERT INTO analytics_events (user_id, session_id, event_name, page_path, beach_slug, metadata_json)
            VALUES (:user_id, :session_id, :event_name, :page_path, :beach_slug, :metadata_json)
            """
        ),
        {
            "user_id": user_id,
            "session_id": payload.session_id,
            "event_name": payload.event_name,
            "page_path": payload.page_path,
            "beach_slug": payload.beach_slug,
            "metadata_json": metadata_json,
        },
    )
    db.commit()
    return {"accepted": True}


@router.get("/admin/analytics/summary", response_model=AnalyticsSummary)
def analytics_summary(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("ADMIN")),
) -> AnalyticsSummary:
    cutoff = (datetime.now(UTC) - timedelta(days=days)).replace(tzinfo=None)
    total = db.execute(
        text("SELECT COUNT(*) FROM analytics_events WHERE created_at >= :cutoff"),
        {"cutoff": cutoff},
    ).scalar_one()
    unique_sessions = db.execute(
        text(
            """
            SELECT COUNT(DISTINCT session_id) FROM analytics_events
            WHERE created_at >= :cutoff AND session_id IS NOT NULL
            """
        ),
        {"cutoff": cutoff},
    ).scalar_one()

    def top_rows(column: str, alias: str) -> list[dict]:
        rows = db.execute(
            text(
                f"""
                SELECT {column} AS {alias}, COUNT(*) AS events
                FROM analytics_events
                WHERE created_at >= :cutoff AND {column} IS NOT NULL
                GROUP BY {column}
                ORDER BY events DESC
                LIMIT 10
                """
            ),
            {"cutoff": cutoff},
        ).mappings().all()
        return [dict(row) for row in rows]

    return AnalyticsSummary(
        total_events=int(total),
        unique_sessions=int(unique_sessions),
        top_pages=top_rows("page_path", "page"),
        top_beaches=top_rows("beach_slug", "beach"),
        top_events=top_rows("event_name", "event"),
    )


@router.post(
    "/media/images",
    response_model=MediaAssetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_community_rate_limit)],
)
async def upload_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_verified_user),
) -> MediaAssetResponse:
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail="Formato inválido. Use JPG, PNG ou WebP.")

    raw = await image.read(settings.media_max_image_mb * 1024 * 1024 + 1)
    if len(raw) > settings.media_max_image_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Imagem maior que o limite permitido.")

    try:
        source = Image.open(BytesIO(raw))
        source.verify()
        source = Image.open(BytesIO(raw))
        source = ImageOps.exif_transpose(source)
        source.thumbnail((2048, 2048))
        if source.mode not in ("RGB", "RGBA"):
            source = source.convert("RGB")
        output = BytesIO()
        source.save(output, format="WEBP", quality=85, method=6)
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Arquivo não contém uma imagem válida.") from exc

    content = output.getvalue()
    media_root = Path(settings.media_root).resolve()
    media_root.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}.webp"
    destination = media_root / stored_name
    destination.write_bytes(content)
    relative_url = f"{settings.media_public_url.rstrip('/')}/{stored_name}"
    public_url = f"{settings.media_public_origin.rstrip('/')}{relative_url}"

    result = db.execute(
        text(
            """
            INSERT INTO media_assets (owner_id, original_name, stored_name, mime_type, size_bytes, public_url)
            VALUES (:owner_id, :original_name, :stored_name, 'image/webp', :size_bytes, :public_url)
            """
        ),
        {
            "owner_id": current_user["id"],
            "original_name": (image.filename or "imagem")[:255],
            "stored_name": stored_name,
            "size_bytes": len(content),
            "public_url": public_url,
        },
    )
    asset_id = int(result.lastrowid)
    db.commit()
    row = db.execute(
        text(
            """
            SELECT id, original_name, mime_type, size_bytes, public_url, created_at
            FROM media_assets WHERE id = :id
            """
        ),
        {"id": asset_id},
    ).mappings().one()
    return MediaAssetResponse.model_validate(dict(row))
