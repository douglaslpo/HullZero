"""
Inicialização de Papéis e Permissões - HullZero

Script para criar papéis e permissões padrão no banco de dados.
"""

from sqlalchemy.orm import Session
from .models import Role, Permission, UserRoleEnum, PermissionEnum

# Mapeamento de papéis para permissões
ROLE_PERMISSIONS = {
    UserRoleEnum.ADMINISTRADOR_SISTEMA: [
        PermissionEnum.MANAGE_USERS,
        PermissionEnum.MANAGE_ROLES,
        PermissionEnum.MANAGE_VESSELS,
        PermissionEnum.MANAGE_SYSTEM,
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_COMPLIANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
        PermissionEnum.CREATE_VESSEL,
        PermissionEnum.EDIT_VESSEL,
        PermissionEnum.DELETE_VESSEL,
        PermissionEnum.REGISTER_MAINTENANCE,
        PermissionEnum.REGISTER_OPERATIONAL_DATA,
        PermissionEnum.REGISTER_INSPECTION,
        PermissionEnum.APPROVE_MAINTENANCE,
        PermissionEnum.APPROVE_COMPLIANCE,
        PermissionEnum.APPROVE_ACTION,
        PermissionEnum.GENERATE_REPORTS,
        PermissionEnum.EXPORT_DATA,
        PermissionEnum.VIEW_AUDIT_LOGS,
        PermissionEnum.VIEW_PREDICTIONS,
        PermissionEnum.VIEW_ADVANCED_PREDICTIONS,
        PermissionEnum.VIEW_EXPLANATIONS,
    ],
    UserRoleEnum.DIRETOR_OPERACOES: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_COMPLIANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
        PermissionEnum.GENERATE_REPORTS,
        PermissionEnum.EXPORT_DATA,
        PermissionEnum.VIEW_PREDICTIONS,
        PermissionEnum.VIEW_ADVANCED_PREDICTIONS,
        PermissionEnum.VIEW_EXPLANATIONS,
        PermissionEnum.VIEW_AUDIT_LOGS,
    ],
    UserRoleEnum.GERENTE_FROTA: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_COMPLIANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
        PermissionEnum.CREATE_VESSEL,
        PermissionEnum.EDIT_VESSEL,
        PermissionEnum.APPROVE_MAINTENANCE,
        PermissionEnum.APPROVE_ACTION,
        PermissionEnum.GENERATE_REPORTS,
        PermissionEnum.EXPORT_DATA,
        PermissionEnum.VIEW_PREDICTIONS,
        PermissionEnum.VIEW_ADVANCED_PREDICTIONS,
        PermissionEnum.VIEW_EXPLANATIONS,
    ],
    UserRoleEnum.OFICIAL_SEGURANCA: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_COMPLIANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
        PermissionEnum.REGISTER_INSPECTION,
        PermissionEnum.APPROVE_COMPLIANCE,
        PermissionEnum.APPROVE_ACTION,
        PermissionEnum.GENERATE_REPORTS,
        PermissionEnum.EXPORT_DATA,
        PermissionEnum.VIEW_PREDICTIONS,
        PermissionEnum.VIEW_EXPLANATIONS,
    ],
    UserRoleEnum.INSPETOR_NORMAM: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_COMPLIANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.REGISTER_INSPECTION,
        PermissionEnum.GENERATE_REPORTS,
        PermissionEnum.VIEW_PREDICTIONS,
    ],
    UserRoleEnum.ENGENHEIRO_NAVAL: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_COMPLIANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
        PermissionEnum.APPROVE_MAINTENANCE,
        PermissionEnum.APPROVE_ACTION,
        PermissionEnum.VIEW_PREDICTIONS,
        PermissionEnum.VIEW_ADVANCED_PREDICTIONS,
        PermissionEnum.VIEW_EXPLANATIONS,
    ],
    UserRoleEnum.CAPITAO_EMBARCAÇÃO: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_COMPLIANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
        PermissionEnum.REGISTER_MAINTENANCE,
        PermissionEnum.REGISTER_OPERATIONAL_DATA,
        PermissionEnum.VIEW_PREDICTIONS,
        PermissionEnum.VIEW_EXPLANATIONS,
        PermissionEnum.GENERATE_REPORTS,
    ],
    UserRoleEnum.IMEDIATO: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_COMPLIANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
        PermissionEnum.REGISTER_OPERATIONAL_DATA,
        PermissionEnum.VIEW_PREDICTIONS,
    ],
    UserRoleEnum.OFICIAL_MAQUINAS: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
        PermissionEnum.REGISTER_OPERATIONAL_DATA,
        PermissionEnum.VIEW_MAINTENANCE,
    ],
    UserRoleEnum.TECNICO_MANUTENCAO: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.REGISTER_MAINTENANCE,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
    ],
    UserRoleEnum.AUDITOR: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_COMPLIANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
        PermissionEnum.GENERATE_REPORTS,
        PermissionEnum.EXPORT_DATA,
        PermissionEnum.VIEW_AUDIT_LOGS,
    ],
    UserRoleEnum.ANALISTA_DADOS: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_COMPLIANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
        PermissionEnum.VIEW_PREDICTIONS,
        PermissionEnum.VIEW_ADVANCED_PREDICTIONS,
        PermissionEnum.GENERATE_REPORTS,
        PermissionEnum.EXPORT_DATA,
    ],
    UserRoleEnum.CONSULTOR: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_COMPLIANCE,
        PermissionEnum.VIEW_MAINTENANCE,
        PermissionEnum.GENERATE_REPORTS,
        PermissionEnum.EXPORT_DATA,
    ],
    UserRoleEnum.OPERADOR: [
        PermissionEnum.VIEW_DASHBOARD,
        PermissionEnum.VIEW_VESSELS,
        PermissionEnum.VIEW_OPERATIONAL_DATA,
        PermissionEnum.REGISTER_OPERATIONAL_DATA,
    ],
    UserRoleEnum.VISUALIZADOR: [
        PermissionEnum.VIEW_DASHBOARD,
    ],
}

# Níveis hierárquicos
ROLE_LEVELS = {
    UserRoleEnum.ADMINISTRADOR_SISTEMA: 1,
    UserRoleEnum.DIRETOR_OPERACOES: 2,
    UserRoleEnum.GERENTE_FROTA: 3,
    UserRoleEnum.OFICIAL_SEGURANCA: 3,
    UserRoleEnum.INSPETOR_NORMAM: 4,
    UserRoleEnum.ENGENHEIRO_NAVAL: 4,
    UserRoleEnum.CAPITAO_EMBARCAÇÃO: 4,
    UserRoleEnum.IMEDIATO: 5,
    UserRoleEnum.OFICIAL_MAQUINAS: 5,
    UserRoleEnum.TECNICO_MANUTENCAO: 5,
    UserRoleEnum.AUDITOR: 3,
    UserRoleEnum.ANALISTA_DADOS: 4,
    UserRoleEnum.CONSULTOR: 4,
    UserRoleEnum.OPERADOR: 5,
    UserRoleEnum.VISUALIZADOR: 5,
}

# Descrições dos papéis
ROLE_DESCRIPTIONS = {
    UserRoleEnum.ADMINISTRADOR_SISTEMA: "Acesso total ao sistema, configurações globais e gestão de usuários",
    UserRoleEnum.DIRETOR_OPERACOES: "Visão estratégica completa da frota e operações",
    UserRoleEnum.GERENTE_FROTA: "Gestão operacional completa da frota",
    UserRoleEnum.OFICIAL_SEGURANCA: "Garantir conformidade com normas de segurança e regulamentações",
    UserRoleEnum.INSPETOR_NORMAM: "Realizar inspeções e verificações de conformidade NORMAM 401",
    UserRoleEnum.ENGENHEIRO_NAVAL: "Análise técnica e engenharia de embarcações",
    UserRoleEnum.CAPITAO_EMBARCAÇÃO: "Comando de embarcação específica",
    UserRoleEnum.IMEDIATO: "Assistência ao capitão, comando em sua ausência",
    UserRoleEnum.OFICIAL_MAQUINAS: "Operação e manutenção de sistemas de propulsão",
    UserRoleEnum.TECNICO_MANUTENCAO: "Execução de manutenções e limpezas",
    UserRoleEnum.AUDITOR: "Auditoria e verificação de conformidade",
    UserRoleEnum.ANALISTA_DADOS: "Análise de dados e geração de insights",
    UserRoleEnum.CONSULTOR: "Acesso limitado para consultoria",
    UserRoleEnum.OPERADOR: "Operação básica e registro de dados",
    UserRoleEnum.VISUALIZADOR: "Apenas visualização de dados públicos",
}

# Descrições das permissões
PERMISSION_DESCRIPTIONS = {
    PermissionEnum.MANAGE_USERS: "Gerenciar usuários do sistema",
    PermissionEnum.MANAGE_ROLES: "Gerenciar papéis e permissões",
    PermissionEnum.MANAGE_VESSELS: "Gerenciar embarcações",
    PermissionEnum.MANAGE_SYSTEM: "Gerenciar configurações do sistema",
    PermissionEnum.VIEW_DASHBOARD: "Visualizar dashboard e KPIs",
    PermissionEnum.VIEW_VESSELS: "Visualizar informações de embarcações",
    PermissionEnum.VIEW_COMPLIANCE: "Visualizar dados de conformidade",
    PermissionEnum.VIEW_MAINTENANCE: "Visualizar histórico de manutenção",
    PermissionEnum.VIEW_OPERATIONAL_DATA: "Visualizar dados operacionais",
    PermissionEnum.CREATE_VESSEL: "Criar novas embarcações",
    PermissionEnum.EDIT_VESSEL: "Editar informações de embarcações",
    PermissionEnum.DELETE_VESSEL: "Excluir embarcações",
    PermissionEnum.REGISTER_MAINTENANCE: "Registrar eventos de manutenção",
    PermissionEnum.REGISTER_OPERATIONAL_DATA: "Registrar dados operacionais",
    PermissionEnum.REGISTER_INSPECTION: "Registrar inspeções NORMAM 401",
    PermissionEnum.APPROVE_MAINTENANCE: "Aprovar manutenções",
    PermissionEnum.APPROVE_COMPLIANCE: "Aprovar verificações de conformidade",
    PermissionEnum.APPROVE_ACTION: "Aprovar ações corretivas",
    PermissionEnum.GENERATE_REPORTS: "Gerar relatórios",
    PermissionEnum.EXPORT_DATA: "Exportar dados",
    PermissionEnum.VIEW_AUDIT_LOGS: "Visualizar logs de auditoria",
    PermissionEnum.VIEW_PREDICTIONS: "Visualizar predições básicas",
    PermissionEnum.VIEW_ADVANCED_PREDICTIONS: "Visualizar predições avançadas",
    PermissionEnum.VIEW_EXPLANATIONS: "Visualizar explicações de modelos de IA",
}


def init_permissions(db: Session):
    """Cria todas as permissões no banco de dados"""
    for permission_enum in PermissionEnum:
        existing = db.query(Permission).filter(Permission.id == permission_enum.value).first()
        if not existing:
            permission = Permission(
                id=permission_enum.value,
                name=permission_enum.value.replace("_", " ").title(),
                description=PERMISSION_DESCRIPTIONS.get(permission_enum, ""),
                category=_get_permission_category(permission_enum)
            )
            db.add(permission)
    db.commit()
    print("✓ Permissões inicializadas")


def init_roles(db: Session):
    """Cria todos os papéis e suas permissões no banco de dados"""
    # Primeiro, garantir que permissões existem
    init_permissions(db)
    
    for role_enum in UserRoleEnum:
        # Criar ou atualizar papel
        role = db.query(Role).filter(Role.id == role_enum.value).first()
        if not role:
            role = Role(
                id=role_enum.value,
                name=role_enum.value.replace("_", " ").title(),
                description=ROLE_DESCRIPTIONS.get(role_enum, ""),
                level=ROLE_LEVELS.get(role_enum, 5)
            )
            db.add(role)
            db.flush()
        
        # Atribuir permissões
        permissions = ROLE_PERMISSIONS.get(role_enum, [])
        for permission_enum in permissions:
            permission = db.query(Permission).filter(Permission.id == permission_enum.value).first()
            if permission and permission not in role.permissions:
                role.permissions.append(permission)
    
    db.commit()
    print("✓ Papéis inicializados")


def _get_permission_category(permission: PermissionEnum) -> str:
    """Determina categoria da permissão"""
    if "MANAGE" in permission.value:
        return "management"
    elif "VIEW" in permission.value:
        return "view"
    elif "REGISTER" in permission.value or "CREATE" in permission.value or "EDIT" in permission.value or "DELETE" in permission.value:
        return "operation"
    elif "APPROVE" in permission.value:
        return "approval"
    elif "GENERATE" in permission.value or "EXPORT" in permission.value:
        return "report"
    else:
        return "other"

