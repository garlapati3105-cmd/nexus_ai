"""
Nexus AI — Notification Repository
Real Supabase operations for: notifications, ai_logs.
"""
from __future__ import annotations
from app.repositories.base import BaseRepository
from app.core.logging import get_logger
from app.core.exceptions import DatabaseOperationException

logger = get_logger("repository.notification")


class NotificationRepository(BaseRepository):
    TABLE_NAME = "notifications"

    def create_notification(
        self,
        title: str,
        message: str,
        notification_type: str = "system",
        severity: str = "info",
        branch_id: str | None = None,
        user_id: str | None = None,
        action_url: str | None = None,
    ) -> dict:
        """Insert a notification record."""
        data = {
            "title": title,
            "message": message,
            "type": notification_type,
            "severity": severity,
            "is_read": False,
        }
        if branch_id:
            data["branch_id"] = branch_id
        if user_id:
            data["user_id"] = user_id
        if action_url:
            data["action_url"] = action_url
        return self.create(data)

    def create_ai_log(
        self,
        agent_name: str,
        message: str,
        log_level: str = "info",
        session_id: str | None = None,
    ) -> dict:
        """Insert an AI log entry. Looks up agent_id by name first."""
        try:
            # Resolve agent_id from agent name
            agent_result = (
                self.db.table("ai_agents")
                .select("id")
                .eq("name", agent_name)
                .limit(1)
                .execute()
            )
            agent_id = agent_result.data[0]["id"] if agent_result.data else None

            data = {
                "agent_id": agent_id,
                "log_level": log_level,
                "message": message,
                "session_id": session_id,
            }
            result = self.db.table("ai_logs").insert(data).execute()
            if result.data:
                return result.data[0]
            raise DatabaseOperationException("create_ai_log", "No data returned")
        except DatabaseOperationException:
            raise
        except Exception as e:
            logger.error(f"create_ai_log failed: {e}")
            raise DatabaseOperationException("create_ai_log", str(e))

    def get_unread_notifications(
        self,
        user_id: str | None = None,
        branch_id: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """Fetch unread notifications."""
        try:
            query = self.db.table(self.TABLE_NAME).select("*").eq("is_read", False)
            if user_id:
                query = query.eq("user_id", user_id)
            if branch_id:
                query = query.eq("branch_id", branch_id)
            query = query.order("created_at", desc=True).limit(limit)
            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"get_unread_notifications failed: {e}")
            raise DatabaseOperationException("get_unread_notifications", str(e))

    def mark_read(self, notification_id: str) -> dict:
        """Mark a notification as read."""
        return self.update(notification_id, {"is_read": True})
