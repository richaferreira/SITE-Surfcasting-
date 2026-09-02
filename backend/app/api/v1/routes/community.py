from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_verified_user
from app.api.dependencies.rate_limit import enforce_community_rate_limit
from app.core.security import require_roles
from app.db import get_db
from app.schemas.community import (
    CatchCreate,
    CatchResponse,
    CommentCreate,
    CommentResponse,
    PostCreate,
    PostResponse,
)
from app.services.notifications import create_notification

router = APIRouter(prefix="/community", tags=["Comunidade"])

POST_SELECT = """
    SELECT p.id, p.author_id, u.name AS author_name, p.title, p.slug, p.excerpt,
           p.content, p.content_type, p.featured_image_url, p.video_url,
           p.published_at, p.created_at,
           (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.id) AS likes,
           (SELECT COUNT(*) FROM post_comments pc WHERE pc.post_id = p.id AND pc.status = 'PUBLICADO') AS comments
    FROM posts p
    JOIN users u ON u.id = p.author_id
"""


@router.get("/posts", response_model=list[PostResponse])
def list_posts(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[PostResponse]:
    rows = db.execute(
        text(
            POST_SELECT
            + " WHERE p.status = 'PUBLICADO' ORDER BY p.published_at DESC, p.created_at DESC LIMIT :limit OFFSET :offset"
        ),
        {"limit": limit, "offset": offset},
    ).mappings().all()
    return [PostResponse.model_validate(dict(row)) for row in rows]


@router.get("/posts/{slug}", response_model=PostResponse)
def get_post(slug: str, db: Session = Depends(get_db)) -> PostResponse:
    row = db.execute(
        text(POST_SELECT + " WHERE p.slug = :slug AND p.status = 'PUBLICADO' LIMIT 1"),
        {"slug": slug},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Publicação não encontrada.")
    return PostResponse.model_validate(dict(row))


@router.post(
    "/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_community_rate_limit)],
)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "AUTHOR")),
) -> PostResponse:
    initial_status = "PUBLICADO" if current_user["role"] == "ADMIN" else "EM_REVISAO"
    published_sql = "CURRENT_TIMESTAMP" if initial_status == "PUBLICADO" else "NULL"
    try:
        result = db.execute(
            text(
                f"""
                INSERT INTO posts (
                    author_id, title, slug, excerpt, content, content_type, status,
                    featured_image_url, video_url, published_at
                ) VALUES (
                    :author_id, :title, :slug, :excerpt, :content, :content_type, :status,
                    :featured_image_url, :video_url, {published_sql}
                )
                """
            ),
            {**payload.model_dump(), "author_id": current_user["id"], "status": initial_status},
        )
        post_id = result.lastrowid
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe uma publicação com esse slug.") from exc

    row = db.execute(text(POST_SELECT + " WHERE p.id = :id"), {"id": post_id}).mappings().one()
    return PostResponse.model_validate(dict(row))


@router.post("/posts/{post_id}/publish", response_model=PostResponse)
def publish_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("ADMIN", "AUTHOR")),
) -> PostResponse:
    post = db.execute(text("SELECT author_id FROM posts WHERE id = :id"), {"id": post_id}).mappings().first()
    if not post:
        raise HTTPException(status_code=404, detail="Publicação não encontrada.")
    if current_user["role"] != "ADMIN" and post["author_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Você só pode publicar conteúdo de sua autoria.")

    db.execute(
        text("UPDATE posts SET status = 'PUBLICADO', published_at = COALESCE(published_at, CURRENT_TIMESTAMP) WHERE id = :id"),
        {"id": post_id},
    )
    db.commit()
    row = db.execute(text(POST_SELECT + " WHERE p.id = :id"), {"id": post_id}).mappings().one()
    return PostResponse.model_validate(dict(row))


@router.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
def list_comments(post_id: int, db: Session = Depends(get_db)) -> list[CommentResponse]:
    rows = db.execute(
        text(
            """
            SELECT c.id, c.post_id, c.author_id, u.name AS author_name, c.content, c.created_at
            FROM post_comments c
            JOIN users u ON u.id = c.author_id
            WHERE c.post_id = :post_id AND c.status = 'PUBLICADO'
            ORDER BY c.created_at ASC
            """
        ),
        {"post_id": post_id},
    ).mappings().all()
    return [CommentResponse.model_validate(dict(row)) for row in rows]


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_community_rate_limit)],
)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_verified_user),
) -> CommentResponse:
    post = db.execute(
        text("SELECT id, author_id, title, slug FROM posts WHERE id = :id AND status = 'PUBLICADO'"),
        {"id": post_id},
    ).mappings().first()
    if not post:
        raise HTTPException(status_code=404, detail="Publicação não encontrada.")

    result = db.execute(
        text("INSERT INTO post_comments (post_id, author_id, content) VALUES (:post_id, :author_id, :content)"),
        {"post_id": post_id, "author_id": current_user["id"], "content": payload.content.strip()},
    )
    comment_id = result.lastrowid
    if post["author_id"] != current_user["id"]:
        create_notification(
            db,
            int(post["author_id"]),
            "POST_COMMENT",
            "Novo comentário na sua publicação",
            f"{current_user['name']} comentou em “{post['title']}”.",
            f"/comunidade#{post['slug']}",
        )
    db.commit()
    row = db.execute(
        text(
            """
            SELECT c.id, c.post_id, c.author_id, u.name AS author_name, c.content, c.created_at
            FROM post_comments c JOIN users u ON u.id = c.author_id
            WHERE c.id = :id
            """
        ),
        {"id": comment_id},
    ).mappings().one()
    return CommentResponse.model_validate(dict(row))


@router.post(
    "/posts/{post_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(enforce_community_rate_limit)],
)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_verified_user),
) -> None:
    post = db.execute(
        text("SELECT id, author_id, title, slug FROM posts WHERE id = :id AND status = 'PUBLICADO'"),
        {"id": post_id},
    ).mappings().first()
    if not post:
        raise HTTPException(status_code=404, detail="Publicação não encontrada.")
    result = db.execute(
        text("INSERT IGNORE INTO post_likes (post_id, user_id) VALUES (:post_id, :user_id)"),
        {"post_id": post_id, "user_id": current_user["id"]},
    )
    if result.rowcount and post["author_id"] != current_user["id"]:
        create_notification(
            db,
            int(post["author_id"]),
            "POST_LIKE",
            "Sua publicação recebeu uma curtida",
            f"{current_user['name']} curtiu “{post['title']}”.",
            f"/comunidade#{post['slug']}",
        )
    db.commit()


@router.delete(
    "/posts/{post_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(enforce_community_rate_limit)],
)
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_verified_user),
) -> None:
    db.execute(
        text("DELETE FROM post_likes WHERE post_id = :post_id AND user_id = :user_id"),
        {"post_id": post_id, "user_id": current_user["id"]},
    )
    db.commit()


@router.get("/catches", response_model=list[CatchResponse])
def list_catches(
    limit: int = Query(default=30, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[CatchResponse]:
    rows = db.execute(
        text(
            """
            SELECT c.id, c.user_id, u.name AS user_name, c.praia_id, p.name AS beach_name,
                   c.species_name, c.bait, c.technique,
                   CAST(c.weight_kg AS DOUBLE) AS weight_kg,
                   CAST(c.length_cm AS DOUBLE) AS length_cm,
                   c.image_url, c.notes, c.caught_at, c.created_at
            FROM catches c
            JOIN users u ON u.id = c.user_id
            LEFT JOIN praias p ON p.id = c.praia_id
            WHERE c.is_public = TRUE
            ORDER BY c.caught_at DESC, c.created_at DESC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    ).mappings().all()
    return [CatchResponse.model_validate(dict(row)) for row in rows]


@router.post(
    "/catches",
    response_model=CatchResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_community_rate_limit)],
)
def create_catch(
    payload: CatchCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_verified_user),
) -> CatchResponse:
    if payload.praia_id is not None:
        beach = db.execute(text("SELECT id FROM praias WHERE id = :id"), {"id": payload.praia_id}).scalar_one_or_none()
        if beach is None:
            raise HTTPException(status_code=404, detail="Praia informada não existe.")

    result = db.execute(
        text(
            """
            INSERT INTO catches (
                user_id, praia_id, species_name, bait, technique, weight_kg,
                length_cm, image_url, notes, caught_at, is_public
            ) VALUES (
                :user_id, :praia_id, :species_name, :bait, :technique, :weight_kg,
                :length_cm, :image_url, :notes, :caught_at, :is_public
            )
            """
        ),
        {**payload.model_dump(), "user_id": current_user["id"]},
    )
    catch_id = result.lastrowid
    db.commit()
    row = db.execute(
        text(
            """
            SELECT c.id, c.user_id, u.name AS user_name, c.praia_id, p.name AS beach_name,
                   c.species_name, c.bait, c.technique,
                   CAST(c.weight_kg AS DOUBLE) AS weight_kg,
                   CAST(c.length_cm AS DOUBLE) AS length_cm,
                   c.image_url, c.notes, c.caught_at, c.created_at
            FROM catches c JOIN users u ON u.id = c.user_id
            LEFT JOIN praias p ON p.id = c.praia_id WHERE c.id = :id
            """
        ),
        {"id": catch_id},
    ).mappings().one()
    return CatchResponse.model_validate(dict(row))
