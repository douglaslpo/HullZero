"""
Mapeador de Nomes de Navios - HullZero

Mapeia nomes de navios dos dados reais para IDs de embarcações no banco de dados.
"""

from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from ..database.models import Vessel
from ..database.repositories import VesselRepository


class VesselNameMapper:
    """
    Mapeia nomes de navios para IDs de embarcações.
    """
    
    # Dicionário de mapeamento conhecido (nome do arquivo/nome do navio → ID ou padrão de busca)
    KNOWN_MAPPINGS = {
        # Mapeamentos diretos conhecidos
        "BRUNO LIMA": ["BRUNO_LIMA", "BRUNO-LIMA", "BRUNOLIMA"],
        "CARLA SILVA": ["CARLA_SILVA", "CARLA-SILVA", "CARLASILVA"],
        "DANIEL PEREIRA": ["DANIEL_PEREIRA", "DANIEL-PEREIRA", "DANIELPEREIRA"],
        "EDUARDO COSTA": ["EDUARDO_COSTA", "EDUARDO-COSTA", "EDUARDOCOSTA"],
        "FABIO SANTOS": ["FABIO_SANTOS", "FABIO-SANTOS", "FABIOSANTOS"],
        "FELIPE RIBEIRO": ["FELIPE_RIBEIRO", "FELIPE-RIBEIRO", "FELIPERIBEIRO"],
        "GABRIELA MARTINS": ["GABRIELA_MARTINS", "GABRIELA-MARTINS", "GABRIELAMARTINS"],
        "GISELLE CARVALHO": ["GISELLE_CARVALHO", "GISELLE-CARVALHO", "GISELLECARVALHO"],
        "HENRIQUE ALVES": ["HENRIQUE_ALVES", "HENRIQUE-ALVES", "HENRIQUEALVES"],
        "LUCAS MEDONCA": ["LUCAS_MEDONCA", "LUCAS-MEDONCA", "LUCASMEDONCA"],
        "MARCOS CAVALCANTI": ["MARCOS_CAVALCANTI", "MARCOS-CAVALCANTI", "MARCOSCAVALCANTI"],
        "MARIA VALENTINA": ["MARIA_VALENTINA", "MARIA-VALENTINA", "MARIAVALENTINA"],
        "PAULO MOURA": ["PAULO_MOURA", "PAULO-MOURA", "PAULOMOURA"],
        "RAFAEL SANTOS": ["RAFAEL_SANTOS", "RAFAEL-SANTOS", "RAFAELSANTOS"],
        "RAUL MARTINS": ["RAUL_MARTINS", "RAUL-MARTINS", "RAULMARTINS"],
        "RICARDO BARBOSA": ["RICARDO_BARBOSA", "RICARDO-BARBOSA", "RICARDOBARBOSA"],
        "RODRIGO PINHEIRO": ["RODRIGO_PINHEIRO", "RODRIGO-PINHEIRO", "RODRIGOPINHEIRO"],
        "ROMARIO SILVA": ["ROMARIO_SILVA", "ROMARIO-SILVA", "ROMARIOSILVA"],
        "THIAGO FERNANDES": ["THIAGO_FERNANDES", "THIAGO-FERNANDES", "THIAGOFERNANDES"],
        "VICTOR OLIVEIRA": ["VICTOR_OLIVEIRA", "VICTOR-OLIVEIRA", "VICTOROLIVEIRA"],
    }
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normaliza nome para comparação (remove acentos, espaços, etc.)
        """
        if not name:
            return ""
        
        # Converter para maiúsculas
        normalized = name.upper().strip()
        
        # Remover acentos (básico)
        replacements = {
            'Á': 'A', 'À': 'A', 'Â': 'A', 'Ã': 'A',
            'É': 'E', 'Ê': 'E',
            'Í': 'I',
            'Ó': 'O', 'Ô': 'O', 'Õ': 'O',
            'Ú': 'U',
            'Ç': 'C'
        }
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remover espaços extras
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    @staticmethod
    def find_vessel_by_name(db: Session, name: str) -> Optional[Vessel]:
        """
        Encontra embarcação por nome (busca flexível).
        
        Estratégias:
        1. Busca exata (case-insensitive)
        2. Busca por substring
        3. Busca normalizada
        4. Busca por padrões conhecidos
        """
        if not name:
            return None
        
        normalized_name = VesselNameMapper.normalize_name(name)
        
        # 1. Busca exata (case-insensitive)
        vessel = db.query(Vessel).filter(
            Vessel.name.ilike(f"%{name}%")
        ).first()
        
        if vessel:
            return vessel
        
        # 2. Busca normalizada
        all_vessels = db.query(Vessel).all()
        for v in all_vessels:
            if VesselNameMapper.normalize_name(v.name) == normalized_name:
                return v
        
        # 3. Busca por substring (normalizada)
        for v in all_vessels:
            v_normalized = VesselNameMapper.normalize_name(v.name)
            if normalized_name in v_normalized or v_normalized in normalized_name:
                return v
        
        # 4. Busca por padrões conhecidos
        if name.upper() in VesselNameMapper.KNOWN_MAPPINGS:
            patterns = VesselNameMapper.KNOWN_MAPPINGS[name.upper()]
            for pattern in patterns:
                for v in all_vessels:
                    v_normalized = VesselNameMapper.normalize_name(v.name)
                    if pattern.upper() in v_normalized or v_normalized in pattern.upper():
                        return v
        
        return None
    
    @staticmethod
    def get_or_create_vessel_by_name(
        db: Session, 
        name: str,
        default_class: str = "Suezmax",
        default_type: str = "tanker"
    ) -> Vessel:
        """
        Obtém ou cria embarcação por nome.
        
        Se não encontrar, cria uma nova embarcação com dados básicos.
        """
        vessel = VesselNameMapper.find_vessel_by_name(db, name)
        
        if vessel:
            return vessel
        
        # Criar nova embarcação
        vessel_data = {
            "name": name,
            "vessel_class": default_class,
            "vessel_type": default_type,
            "status": "active",
            "fleet_category": default_class.lower(),
        }
        
        vessel = VesselRepository.create(db, vessel_data)
        print(f"✅ Criada nova embarcação: {name} (ID: {vessel.id})")
        
        return vessel
    
    @staticmethod
    def build_name_mapping(db: Session) -> Dict[str, str]:
        """
        Constrói dicionário de mapeamento nome → vessel_id.
        
        Returns:
            Dict com chave sendo nome normalizado e valor sendo vessel_id
        """
        mapping = {}
        vessels = db.query(Vessel).all()
        
        for vessel in vessels:
            # Adicionar nome original
            normalized = VesselNameMapper.normalize_name(vessel.name)
            mapping[normalized] = vessel.id
            
            # Adicionar variações conhecidas
            if vessel.name.upper() in VesselNameMapper.KNOWN_MAPPINGS:
                for variant in VesselNameMapper.KNOWN_MAPPINGS[vessel.name.upper()]:
                    mapping[VesselNameMapper.normalize_name(variant)] = vessel.id
        
        return mapping
    
    @staticmethod
    def get_vessel_id_from_name(db: Session, name: str) -> Optional[str]:
        """
        Obtém vessel_id a partir do nome (método rápido usando cache).
        """
        vessel = VesselNameMapper.find_vessel_by_name(db, name)
        return vessel.id if vessel else None

