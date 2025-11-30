"""
Módulo de Autenticação e Autorização - HullZero
"""

from .models import (
    User,
    Role,
    Permission,
    AuditLog,
    RefreshToken,
    UserRoleEnum,
    PermissionEnum
)
from .auth_service import AuthService
from .dependencies import (
    get_current_user,
    get_current_active_user,
    require_permission,
    require_role,
    require_any_role,
    can_access_vessel
)

__all__ = [
    "User",
    "Role",
    "Permission",
    "AuditLog",
    "RefreshToken",
    "UserRoleEnum",
    "PermissionEnum",
    "AuthService",
    "get_current_user",
    "get_current_active_user",
    "require_permission",
    "require_role",
    "require_any_role",
    "can_access_vessel",
]
