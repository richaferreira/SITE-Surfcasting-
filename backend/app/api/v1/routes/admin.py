import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.db import get_db
from app.schemas.admin import (
    AdminDashboard,
    AdminUser,
    ChangeActiveRequest,
    ChangePostStatusRequest,
    ChangeRoleRequest,
)

router = APIRouter(prefix="/admin", tags=["Backoffice"])
admin_only = require_roles("ADMIN")


def _audit(db: Session, user_id: int, action: str, entity_type: str, entity_id: int, metadata: dict) -> None:
    db.execute(
        text(
            """
            INSERT INTO audit_logs (user_id, action, entity_type, entity_id, metadata_json)
            VALUES (:user_id, :action, :entity_type, :entity_id, :metadata)
            """
        ),
        {
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "metadata": json.dumps(metadata, ensure_ascii=False),
        },
    )


@router.get("/dashboard", response_model=AdminDashboard)
def dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only),
) -> AdminDashboard:
    del current_user
    row = db.execute(
        text(
            """
            SELECT
                (SELECT COUNT(*) FROM users) AS users,
                (SELECT COUNT(*) FROM users WHERE is_active = TRUE) AS active_users,
                (SELECT COUNT(*) FROM praias) AS beaches,
                (SELECT COUNT(*) FROM praias WHERE is_published = TRUE) AS published_beaches,
                (SELECT COUNT(*) FROM posts) AS posts,
                (SELECT COUNT(*) FROM posts WHERE status = 'PUBLICADO') AS published_posts,
                (SELECT COUNT(*) FROM catches) AS catches,
                (SELECT COUNT(*) FROM post_comments WHERE status = 'PUBLICADO') AS comments
            """
        )
    ).mappings().one()
    return AdminDashboard.model_validate(dict(row))


@router.get("/users", response_model=list[AdminUser])
def users(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only),
) -> list[AdminUser]:
    del current_user
    rows = db.execute(
        text(
            """
            SELECT u.id, u.name, u.username, u.email, r.code AS role, u.is_active
            FROM users u JOIN roles r ON r.id = u.role_id
            ORDER BY u.created_at DESC LIMIT :limit
            """
        ),
        {"limit": limit},
    ).mappings().all()
    return [AdminUser.model_validate(dict(row)) for row in rows]


@router.patch("/users/{user_id}/role", response_model=AdminUser)
def change_role(
    user_id: int,
    payload: ChangeRoleRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only),
) -> AdminUser:
    if user_id == current_user["id"] and payload.role != "ADMIN":
        raise HTTPException(status_code=400, detail="O administrador autenticado não pode remover o próprio acesso.")

    role_id = db.execute(text("SELECT id FROM roles WHERE code = :role"), {"role": payload.role}).scalar_one_or_none()
    if role_id is None:
        raise HTTPException(status_code=400, detail="Perfil inválido.")

    result = db.execute(text("UPDATE users SET role_id = :role_id WHERE id = :user_id"), {"role_id": role_id, "user_id": user_id})
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    _audit(db, current_user["id"], "change_role", "user", user_id, {"role": payload.role})
    db.commit()
    row = db.execute(
        text("SELECT u.id, u.name, u.username, u.email, r.code AS role, u.is_active FROM users u JOIN roles r ON r.id = u.role_id WHERE u.id = :id"),
        {"id": user_id},
    ).mappings().one()
    return AdminUser.model_validate(dict(row))


@router.patch("/users/{user_id}/active", response_model=AdminUser)
def change_active(
    user_id: int,
    payload: ChangeActiveRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only),
) -> AdminUser:
    if user_id == current_user["id"] and not payload.is_active:
        raise HTTPException(status_code=400, detail="O administrador autenticado não pode desativar a própria conta.")
    result = db.execute(text("UPDATE users SET is_active = :active WHERE id = :id"), {"active": payload.is_active, "id": user_id})
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    _audit(db, current_user["id"], "change_active", "user", user_id, {"is_active": payload.is_active})
    db.commit()
    row = db.execute(
        text("SELECT u.id, u.name, u.username, u.email, r.code AS role, u.is_active FROM users u JOIN roles r ON r.id = u.role_id WHERE u.id = :id"),
        {"id": user_id},
    ).mappings().one()
    return AdminUser.model_validate(dict(row))


@router.patch("/posts/{post_id}/status")
def change_post_status(
    post_id: int,
    payload: ChangePostStatusRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only),
) -> dict[str, object]:
    published_at = "CURRENT_TIMESTAMP" if payload.status == "PUBLICADO" else "published_at"
    result = db.execute(
        text(f"UPDATE posts SET status = :status, published_at = {published_at} WHERE id = :id"),
        {"status": payload.status, "id": post_id},
    )
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(status_code=404, detail="Publicação não encontrada.")
    _audit(db, current_user["id"], "change_post_status", "post", post_id, {"status": payload.status})
    db.commit()
    return {"id": post_id, "status": payload.status}


@router.delete("/comments/{comment_id}")
def hide_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(admin_only),
) -> dict[str, object]:
    result = db.execute(text("UPDATE post_comments SET status = 'OCULTO' WHERE id = :id"), {"id": comment_id})
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(status_code=404, detail="Comentário não encontrado.")
    _audit(db, current_user["id"], "hide_comment", "comment", comment_id, {})
    db.commit()
    return {"id": comment_id, "status": "OCULTO"}
