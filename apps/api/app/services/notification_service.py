"""
Nexus AI — Notification Service
Creates system notifications and AI log entries in the real database.
"""
from __future__ import annotations
from app.repositories.notification_repo import NotificationRepository
from app.core.logging import get_logger

logger = get_logger("service.notification")


class NotificationService:
    def __init__(self):
        self.repo = NotificationRepository()

    def notify_branch(
        self,
        branch_id: str,
        title: str,
        message: str,
        severity: str = "info",
        notification_type: str = "system",
    ) -> dict:
        """Create a notification targeted at a specific branch."""
        result = self.repo.create_notification(
            title=title,
            message=message,
            notification_type=notification_type,
            severity=severity,
            branch_id=branch_id,
        )
        logger.info(f"Branch notification created: {title} → branch {branch_id}")
        return result

    def create_ai_log(
        self,
        agent_name: str,
        message: str,
        log_level: str = "info",
        session_id: str | None = None,
    ) -> dict | None:
        """Create an AI log entry in the ai_logs table."""
        try:
            result = self.repo.create_ai_log(
                agent_name=agent_name,
                message=message,
                log_level=log_level,
                session_id=session_id,
            )
            logger.info(f"AI Log: [{agent_name}] {message}")
            return result
        except Exception as e:
            # AI logging is non-critical; don't crash the workflow
            logger.warning(f"AI log creation failed (non-fatal): {e}")
            return None

    def get_unread(self, branch_id: str | None = None, limit: int = 50) -> list[dict]:
        """Get unread notifications."""
        return self.repo.get_unread_notifications(branch_id=branch_id, limit=limit)

    def mark_read(self, notification_id: str) -> dict:
        """Mark a notification as read."""
        return self.repo.mark_read(notification_id)
