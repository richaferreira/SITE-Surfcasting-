from sqlalchemy import text
from sqlalchemy.orm import Session


def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    action_url: str | None = None,
) -> None:
    db.execute(
        text(
            """
            INSERT INTO notifications (user_id, notification_type, title, message, action_url)
            VALUES (:user_id, :notification_type, :title, :message, :action_url)
            """
        ),
        {
            "user_id": user_id,
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "action_url": action_url,
        },
    )
