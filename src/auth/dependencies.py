"""
Dependências de Autenticação - HullZero

Dependências FastAPI para autenticação e autorização.
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import get_db
from .auth_service import AuthService
from .models import User, UserRoleEnum, PermissionEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtém usuário atual a partir do token JWT"""
    payload = AuthService.decode_token(token)
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Obtém usuário ativo atual"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    return current_user


def require_permission(permission: PermissionEnum):
    """Dependency factory para verificar permissão"""
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if not AuthService.has_permission(db, current_user.id, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão necessária: {permission.value}"
            )
        return current_user
    return permission_checker


def require_role(role: UserRoleEnum):
    """Dependency factory para verificar papel"""
    async def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if not AuthService.has_role(db, current_user.id, role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Papel necessário: {role.value}"
            )
        return current_user
    return role_checker


def require_any_role(roles: List[UserRoleEnum]):
    """Dependency factory para verificar qualquer um dos papéis"""
    async def roles_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if not AuthService.has_any_role(db, current_user.id, roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Um dos seguintes papéis é necessário: {[r.value for r in roles]}"
            )
        return current_user
    return roles_checker


def can_access_vessel(vessel_id: str):
    """Dependency factory para verificar acesso à embarcação"""
    async def vessel_access_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if not AuthService.can_access_vessel(db, current_user.id, vessel_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado a esta embarcação"
            )
        return current_user
    return vessel_access_checker

