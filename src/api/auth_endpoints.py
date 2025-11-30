"""
Endpoints de Autenticação - HullZero

Endpoints para login, logout, refresh token e gestão de usuários.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

try:
    from ..database import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    # Criar get_db dummy se não disponível
    def get_db():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados não disponível"
        )

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Tentar importar módulos de autenticação
try:
    from ..auth import (
        AuthService,
        User,
        UserRoleEnum,
        PermissionEnum,
        get_current_user,
        get_current_active_user,
        require_permission,
        require_role
    )
    AUTH_AVAILABLE = True
except ImportError as e:
    AUTH_AVAILABLE = False
    # Criar dummies para evitar erros de importação
    AuthService = None
    User = None
    UserRoleEnum = None
    PermissionEnum = None
    get_current_user = None
    get_current_active_user = None
    require_permission = None
    require_role = None
    print(f"⚠️  Autenticação não disponível: {e}")


# Schemas Pydantic
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    employee_id: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    employee_id: Optional[str]
    department: Optional[str]
    position: Optional[str]
    roles: List[str]
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class RoleAssign(BaseModel):
    role_id: str


# Endpoints
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica usuário e retorna tokens JWT.
    
    Usa OAuth2PasswordRequestForm para compatibilidade com frontend.
    """
    if not AUTH_AVAILABLE or AuthService is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema de autenticação não disponível. Verifique se as dependências estão instaladas."
        )
    
    if not DB_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados não disponível"
        )
    
    try:
        # Autenticar usuário (métodos são estáticos)
        user = AuthService.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Atualizar último login
        if hasattr(user, 'last_login'):
            user.last_login = datetime.utcnow()
            db.commit()
        
        # Criar tokens (métodos são estáticos)
        access_token = AuthService.create_access_token(
            data={"sub": user.id, "username": user.username}
        )
        
        refresh_token = AuthService.create_refresh_token(
            data={"sub": user.id, "username": user.username}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60  # 30 minutos em segundos
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Erro ao autenticar: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ Erro na autenticação: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao processar autenticação: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Renova access token usando refresh token"""
    try:
        payload = AuthService.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário inválido ou inativo"
            )
        
        # Criar novo access token
        new_access_token = AuthService.create_access_token(
            data={"sub": user.id, "username": user.username}
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,  # Refresh token não muda
            "token_type": "bearer",
            "expires_in": 30 * 60
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    request: Request,
    db: Session = Depends(get_db)
):
    """Retorna informações do usuário atual"""
    if not AUTH_AVAILABLE or AuthService is None or User is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema de autenticação não disponível"
        )
    
    # Obter token do header Authorization
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Decodificar token
        payload = AuthService.decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Buscar usuário
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado ou inativo"
            )
        
        roles = AuthService.get_user_roles(db, user.id)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            employee_id=user.employee_id,
            department=user.department,
            position=user.position,
            roles=roles
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        employee_id=current_user.employee_id,
        department=current_user.department,
        position=current_user.position,
        roles=roles
    )


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Cria novo usuário (requer permissão MANAGE_USERS)"""
    if not AUTH_AVAILABLE or PermissionEnum is None or require_permission is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema de autenticação não disponível"
        )
    
    # Verificar permissão manualmente
    from fastapi import Request
    request = Request({})
    try:
        current_user = await require_permission(PermissionEnum.MANAGE_USERS)(request, db)
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    # Verificar se username já existe
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já existe"
        )
    
    # Verificar se email já existe
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já existe"
        )
    
    # Criar usuário
    hashed_password = AuthService.get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        employee_id=user_data.employee_id,
        department=user_data.department,
        position=user_data.position,
        phone=user_data.phone,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
        employee_id=new_user.employee_id,
        department=new_user.department,
        position=new_user.position,
        roles=[]
    )


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if not AUTH_AVAILABLE or PermissionEnum is None or require_permission is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema de autenticação não disponível"
        )
    """Lista usuários (requer permissão MANAGE_USERS)"""
    users = db.query(User).offset(skip).limit(limit).all()
    result = []
    for user in users:
        roles = AuthService.get_user_roles(db, user.id)
        result.append(UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            employee_id=user.employee_id,
            department=user.department,
            position=user.position,
            roles=roles
        ))
    return result


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    if not AUTH_AVAILABLE or PermissionEnum is None or require_permission is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema de autenticação não disponível"
        )
    """Atualiza usuário (requer permissão MANAGE_USERS)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Atualizar campos fornecidos
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.department is not None:
        user.department = user_data.department
    if user_data.position is not None:
        user.position = user_data.position
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    roles = AuthService.get_user_roles(db, user.id)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        employee_id=user.employee_id,
        department=user.department,
        position=user.position,
        roles=roles
    )


@router.post("/users/{user_id}/roles", response_model=UserResponse)
async def assign_role(
    user_id: str,
    role_data: RoleAssign,
    db: Session = Depends(get_db)
):
    if not AUTH_AVAILABLE or PermissionEnum is None or require_permission is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema de autenticação não disponível"
        )
    """Atribui papel a usuário (requer permissão MANAGE_USERS)"""
    from ..auth.models import Role
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    role = db.query(Role).filter(Role.id == role_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Papel não encontrado"
        )
    
    # Adicionar papel se não tiver
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
    
    roles = AuthService.get_user_roles(db, user.id)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        employee_id=user.employee_id,
        department=user.department,
        position=user.position,
        roles=roles
    )


@router.get("/roles", response_model=List[dict])
async def list_roles(
    db: Session = Depends(get_db)
):
    """Lista todos os papéis disponíveis"""
    if not AUTH_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema de autenticação não disponível"
        )
    
    from ..auth.models import Role
    roles = db.query(Role).all()
    return [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "level": role.level
        }
        for role in roles
    ]


@router.delete("/users/{user_id}/roles/{role_id}", response_model=UserResponse)
async def remove_role(
    user_id: str,
    role_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Remove papel de usuário (requer permissão MANAGE_USERS)"""
    if not AUTH_AVAILABLE or PermissionEnum is None or require_permission is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema de autenticação não disponível"
        )
    
    # Verificar permissão
    try:
        current_user = await require_permission(PermissionEnum.MANAGE_USERS)(request, db)
    except:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )
    
    from ..auth.models import Role
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Papel não encontrado"
        )
    
    # Remover papel se tiver
    if role in user.roles:
        user.roles.remove(role)
        db.commit()
    
    roles = AuthService.get_user_roles(db, user.id)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        employee_id=user.employee_id,
        department=user.department,
        position=user.position,
        roles=roles
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    request: Request,
    db: Session = Depends(get_db)
):
    if not AUTH_AVAILABLE or get_current_active_user is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sistema de autenticação não disponível"
        )
    
    # Obter usuário atual (mesma lógica do /me)
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = AuthService.decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user or not current_user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido")
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    """Altera senha do usuário atual"""
    # Verificar senha atual
    if not AuthService.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Atualizar senha
    current_user.hashed_password = AuthService.get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Senha alterada com sucesso"}

