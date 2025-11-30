"""
Serviço de Autenticação e Autorização - HullZero

Implementa lógica de autenticação JWT e verificação de permissões.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .models import User, Role, Permission, UserRoleEnum, PermissionEnum
from ..config import (
    SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

# Configuração de segurança (agora usando variáveis de ambiente)
ALGORITHM = JWT_ALGORITHM

# Contexto para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Serviço de autenticação"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha está correta"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # Fallback para bcrypt direto se passlib falhar
            import bcrypt
            try:
                return bcrypt.checkpw(
                    plain_password.encode('utf-8'),
                    hashed_password.encode('utf-8')
                )
            except Exception:
                return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Gera hash da senha"""
        try:
            return pwd_context.hash(password)
        except Exception:
            # Fallback para bcrypt direto se passlib falhar
            import bcrypt
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Cria token JWT de acesso"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Cria token JWT de refresh"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decodifica e valida token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Autentica usuário"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )
        return user
    
    @staticmethod
    def get_user_permissions(db: Session, user_id: str) -> List[str]:
        """Obtém todas as permissões do usuário através de seus papéis"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.id)
        
        return list(permissions)
    
    @staticmethod
    def get_user_roles(db: Session, user_id: str) -> List[str]:
        """Obtém todos os papéis do usuário"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        return [role.id for role in user.roles]
    
    @staticmethod
    def has_permission(db: Session, user_id: str, permission: PermissionEnum) -> bool:
        """Verifica se usuário tem permissão específica"""
        permissions = AuthService.get_user_permissions(db, user_id)
        return permission.value in permissions
    
    @staticmethod
    def has_role(db: Session, user_id: str, role: UserRoleEnum) -> bool:
        """Verifica se usuário tem papel específico"""
        roles = AuthService.get_user_roles(db, user_id)
        return role.value in roles
    
    @staticmethod
    def has_any_role(db: Session, user_id: str, roles: List[UserRoleEnum]) -> bool:
        """Verifica se usuário tem algum dos papéis especificados"""
        user_roles = AuthService.get_user_roles(db, user_id)
        role_values = [role.value for role in roles]
        return any(role in role_values for role in user_roles)
    
    @staticmethod
    def can_access_vessel(db: Session, user_id: str, vessel_id: str) -> bool:
        """Verifica se usuário pode acessar embarcação específica"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Administradores e gerentes têm acesso a todas
        if AuthService.has_any_role(
            db, user_id, 
            [UserRoleEnum.ADMINISTRADOR_SISTEMA, UserRoleEnum.DIRETOR_OPERACOES, UserRoleEnum.GERENTE_FROTA]
        ):
            return True
        
        # Verifica se usuário está atribuído à embarcação
        # Usar query direta na tabela user_vessels para evitar import circular
        from sqlalchemy import text
        result = db.execute(
            text("SELECT 1 FROM user_vessels WHERE user_id = :user_id AND vessel_id = :vessel_id"),
            {"user_id": user_id, "vessel_id": vessel_id}
        ).first()
        return result is not None

