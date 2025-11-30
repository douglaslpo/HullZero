"""
Modelos de Autenticação e Autorização - HullZero

Define modelos para usuários, papéis e permissões.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from enum import Enum

# Usar Base do models_normalized se disponível, senão do models
try:
    from ..database.models_normalized import Base
except ImportError:
    try:
        from ..database.models import Base
    except ImportError:
        # Fallback: criar Base próprio se necessário
        from sqlalchemy.ext.declarative import declarative_base
        Base = declarative_base()


# Tabela de relacionamento N:N entre usuários e papéis
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('role_id', String, ForeignKey('roles.id'), primary_key=True)
)

# Tabela de relacionamento N:N entre papéis e permissões
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', String, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', String, ForeignKey('permissions.id'), primary_key=True)
)

# Tabela de relacionamento N:N entre usuários e embarcações (atribuição)
# Nota: A referência a 'vessels' será criada quando as tabelas forem criadas
user_vessels = Table(
    'user_vessels',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('vessel_id', String, primary_key=True),  # Referência será adicionada após criação de vessels
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('assigned_by', String, ForeignKey('users.id'))
)


class UserRoleEnum(str, Enum):
    """Enum de papéis de usuário"""
    ADMINISTRADOR_SISTEMA = "administrador_sistema"
    DIRETOR_OPERACOES = "diretor_operacoes"
    GERENTE_FROTA = "gerente_frota"
    OFICIAL_SEGURANCA = "oficial_seguranca"
    INSPETOR_NORMAM = "inspetor_normam"
    ENGENHEIRO_NAVAL = "engenheiro_naval"
    CAPITAO_EMBARCAÇÃO = "capitao_embarcacao"
    IMEDIATO = "imediato"
    OFICIAL_MAQUINAS = "oficial_maquinas"
    TECNICO_MANUTENCAO = "tecnico_manutencao"
    AUDITOR = "auditor"
    ANALISTA_DADOS = "analista_dados"
    CONSULTOR = "consultor"
    OPERADOR = "operador"
    VISUALIZADOR = "visualizador"


class PermissionEnum(str, Enum):
    """Enum de permissões"""
    # Gestão
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_VESSELS = "manage_vessels"
    MANAGE_SYSTEM = "manage_system"
    
    # Visualização
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_VESSELS = "view_vessels"
    VIEW_COMPLIANCE = "view_compliance"
    VIEW_MAINTENANCE = "view_maintenance"
    VIEW_OPERATIONAL_DATA = "view_operational_data"
    
    # Operações
    CREATE_VESSEL = "create_vessel"
    EDIT_VESSEL = "edit_vessel"
    DELETE_VESSEL = "delete_vessel"
    REGISTER_MAINTENANCE = "register_maintenance"
    REGISTER_OPERATIONAL_DATA = "register_operational_data"
    REGISTER_INSPECTION = "register_inspection"
    
    # Aprovações
    APPROVE_MAINTENANCE = "approve_maintenance"
    APPROVE_COMPLIANCE = "approve_compliance"
    APPROVE_ACTION = "approve_action"
    
    # Relatórios
    GENERATE_REPORTS = "generate_reports"
    EXPORT_DATA = "export_data"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    
    # Predições
    VIEW_PREDICTIONS = "view_predictions"
    VIEW_ADVANCED_PREDICTIONS = "view_advanced_predictions"
    VIEW_EXPLANATIONS = "view_explanations"


class User(Base):
    """Modelo de Usuário"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Informações adicionais
    employee_id = Column(String(50), unique=True, index=True)  # Matrícula/ID do funcionário
    department = Column(String(100))  # Departamento
    position = Column(String(100))  # Cargo
    phone = Column(String(20))
    
    # Certificações (para papéis regulatórios)
    certifications = Column(Text)  # JSON com certificações
    certification_expiry = Column(DateTime)  # Data de expiração da certificação principal
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relacionamentos
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    # assigned_vessels será configurado dinamicamente após importar Vessel
    audit_logs = relationship("AuditLog", back_populates="user")


class Role(Base):
    """Modelo de Papel (Role)"""
    __tablename__ = "roles"
    
    id = Column(String(50), primary_key=True)  # Usa o enum value
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    level = Column(Integer, nullable=False)  # Nível hierárquico (1-5)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    """Modelo de Permissão"""
    __tablename__ = "permissions"
    
    id = Column(String(50), primary_key=True)  # Usa o enum value
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))  # 'management', 'view', 'operation', 'approval', etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class AuditLog(Base):
    """Modelo de Log de Auditoria"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Informações da ação
    action = Column(String(100), nullable=False, index=True)  # 'create', 'update', 'delete', 'view', etc.
    resource_type = Column(String(100), nullable=False, index=True)  # 'vessel', 'maintenance', 'compliance', etc.
    resource_id = Column(String, index=True)  # ID do recurso afetado
    
    # Dados
    details = Column(Text)  # JSON com detalhes da ação
    changes = Column(Text)  # JSON com mudanças (antes/depois)
    
    # Metadados
    ip_address = Column(String(45))  # IPv4 ou IPv6
    user_agent = Column(String(500))
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relacionamentos
    user = relationship("User", back_populates="audit_logs")


class RefreshToken(Base):
    """Modelo de Refresh Token para JWT"""
    __tablename__ = "refresh_tokens"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    
    # Expiração
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Revogação
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime)

