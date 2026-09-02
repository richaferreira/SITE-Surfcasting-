from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.db import get_db
from app.services.health import check_dependencies
from app.services.observability import metrics

router = APIRouter(prefix="/admin/monitoring", tags=["Admin - Monitoramento"])


@router.get("")
def monitoring_snapshot(
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles("ADMIN")),
) -> dict:
    dependencies = check_dependencies().as_dict()
    counts = db.execute(
        text(
            """
            SELECT
              (SELECT COUNT(*) FROM users WHERE is_active = TRUE) AS active_users,
              (SELECT COUNT(*) FROM praias WHERE is_published = TRUE) AS published_beaches,
              (SELECT COUNT(*) FROM community_reports WHERE status IN ('ABERTO', 'EM_ANALISE')) AS open_reports,
              (SELECT COUNT(*) FROM notifications WHERE read_at IS NULL) AS unread_notifications,
              (SELECT COUNT(*) FROM media_assets) AS media_assets,
              (SELECT COUNT(*) FROM analytics_events WHERE created_at >= UTC_TIMESTAMP() - INTERVAL 1 DAY) AS analytics_events_24h
            """
        )
    ).mappings().one()
    return {
        "dependencies": dependencies,
        "runtime": metrics.snapshot(),
        "database": dict(counts),
    }
