from fastapi import Depends, HTTPException

from app.core.security import get_current_user


def require_verified_user(current_user: dict = Depends(get_current_user)) -> dict:
    if not current_user.get("email_verified_at"):
        raise HTTPException(
            status_code=403,
            detail="Confirme seu e-mail antes de publicar ou interagir na comunidade.",
        )
    return current_user
