from fastapi import HTTPException, status

class AuthenticationError(HTTPException):
    """
    Custom exception for authentication errors.
    Used when credentials cannot be validated.
    """
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class PermissionDenied(HTTPException):
    """
    Custom exception for permission errors.
    Used when user doesn't have required permissions.
    """
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )