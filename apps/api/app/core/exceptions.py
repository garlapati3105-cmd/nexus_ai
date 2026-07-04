"""
Nexus AI — Custom Exception Hierarchy
Provides enterprise-grade error classification for the entire backend.
"""
from fastapi import HTTPException, status


class NexusBaseException(HTTPException):
    """Base exception for all Nexus AI backend errors."""
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)


class EntityNotFoundException(NexusBaseException):
    """Raised when a database entity is not found."""
    def __init__(self, entity: str, entity_id: str):
        super().__init__(
            detail=f"{entity} with ID '{entity_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InsufficientStockException(NexusBaseException):
    """Raised when inventory does not have enough stock."""
    def __init__(self, branch_id: str, medicine_id: str, available: int, requested: int):
        super().__init__(
            detail=(
                f"Insufficient stock at branch '{branch_id}' for medicine '{medicine_id}'. "
                f"Available: {available}, Requested: {requested}."
            ),
            status_code=status.HTTP_409_CONFLICT,
        )


class DatabaseOperationException(NexusBaseException):
    """Raised when a database operation fails unexpectedly."""
    def __init__(self, operation: str, detail: str = ""):
        super().__init__(
            detail=f"Database operation '{operation}' failed. {detail}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ValidationException(NexusBaseException):
    """Raised for business rule validation failures."""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class TransferConflictException(NexusBaseException):
    """Raised when a transfer cannot be processed."""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
        )
