"""
Nexus AI — Employee Repository
Real Supabase operations for: employees, users.
"""
from __future__ import annotations
from app.repositories.base import BaseRepository
from app.core.logging import get_logger
from app.core.exceptions import DatabaseOperationException

logger = get_logger("repository.employee")


class EmployeeRepository(BaseRepository):
    TABLE_NAME = "employees"

    def get_employee_by_user_id(self, user_id: str) -> dict | None:
        """Fetch employee record by their linked user_id."""
        try:
            result = (
                self.db.table(self.TABLE_NAME)
                .select("*")
                .eq("user_id", user_id)
                .limit(1)
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"get_employee_by_user_id failed: {e}")
            raise DatabaseOperationException("get_employee_by_user_id", str(e))

    def get_employees_by_branch(self, branch_id: str, offset: int = 0, limit: int = 50) -> list[dict]:
        """Fetch all employees for a branch."""
        return self.list(filters={"branch_id": branch_id}, offset=offset, limit=limit)

    def get_any_cashier_for_branch(self, branch_id: str) -> str | None:
        """Fetch the first active employee's user_id to use as cashier fallback."""
        try:
            result = (
                self.db.table(self.TABLE_NAME)
                .select("user_id")
                .eq("branch_id", branch_id)
                .eq("status", "active")
                .limit(1)
                .execute()
            )
            return result.data[0]["user_id"] if result.data else None
        except Exception as e:
            logger.error(f"get_any_cashier_for_branch failed: {e}")
            return None
