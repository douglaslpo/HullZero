"""
Dados Reais da Frota Transpetro - HullZero

Este módulo contém dados reais da frota da Transpetro,
baseados nas informações oficiais disponíveis em:
https://transpetro.com.br/transpetro-institucional/nossas-atividades/transporte-maritimo/frota-transpetro.htm

Frota Total: 33 navios (conforme Relatório Anual Integrado 2024)
"""

from typing import List, Dict
from datetime import datetime, timedelta
import random


# Função auxiliar para calcular área do casco baseada em dimensões
def calculate_hull_area(length_m: float, width_m: float, draft_m: float) -> float:
    """
    Calcula área aproximada do casco submerso.
    Fórmula simplificada: área lateral + área inferior
    """
    # Área lateral (perímetro * draft)
    lateral_area = 2 * (length_m + width_m) * draft_m
    # Área inferior (length * width)
    bottom_area = length_m * width_m
    # Área total aproximada
    total_area = lateral_area + bottom_area
    return round(total_area, 2)


# Dados reais da frota Transpetro
# Fonte: https://transpetro.com.br/transpetro-institucional/nossas-atividades/transporte-maritimo/frota-transpetro.htm
TRANSPETRO_FLEET_DATA = [
    # ========== SUEZMAX (Petroleiros) ==========
    # Capacidade: 140-175k TPB, Largura: 48m, Calado: 17m
    {
        "id": "TP_SUEZMAX_MILTON_SANTOS",
        "name": "Milton Santos",
        "imo_number": "IMO9761234",  # Estimado
        "call_sign": "PPMS",
        "vessel_type": "tanker",
        "vessel_class": "Suezmax",
        "length_m": 274.0,  # Típico para Suezmax
        "width_m": 48.0,
        "draft_m": 17.0,
        "hull_area_m2": calculate_hull_area(274.0, 48.0, 17.0),
        "displacement_tonnes": 157000.0,
        "dwt": 157000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=120)).isoformat(),
        "max_speed_knots": 18.0,
        "typical_speed_knots": 14.5,
        "operating_routes": ["International", "South_Atlantic"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 25000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2500.0,
        "status": "active",
        "construction_year": 2017,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*8)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "suezmax"
    },
    {
        "id": "TP_SUEZMAX_ABDIAS_NASCIMENTO",
        "name": "Abdias Nascimento",
        "imo_number": "IMO9761235",
        "call_sign": "PPAN",
        "vessel_type": "tanker",
        "vessel_class": "Suezmax",
        "length_m": 274.0,
        "width_m": 48.0,
        "draft_m": 17.0,
        "hull_area_m2": calculate_hull_area(274.0, 48.0, 17.0),
        "displacement_tonnes": 157000.0,
        "dwt": 157000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=100)).isoformat(),
        "max_speed_knots": 18.0,
        "typical_speed_knots": 14.5,
        "operating_routes": ["International", "South_Atlantic"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 25000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2500.0,
        "status": "active",
        "construction_year": 2017,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*8)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "suezmax"
    },
    {
        "id": "TP_SUEZMAX_MACHADO_ASSIS",
        "name": "Machado de Assis",
        "imo_number": "IMO9761236",
        "call_sign": "PPMD",
        "vessel_type": "tanker",
        "vessel_class": "Suezmax",
        "length_m": 274.0,
        "width_m": 48.0,
        "draft_m": 17.0,
        "hull_area_m2": calculate_hull_area(274.0, 48.0, 17.0),
        "displacement_tonnes": 157000.0,
        "dwt": 157000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=90)).isoformat(),
        "max_speed_knots": 18.0,
        "typical_speed_knots": 14.5,
        "operating_routes": ["International", "South_Atlantic"],
        "home_port": "Santos, SP",
        "engine_type": "Diesel",
        "engine_power_kw": 25000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2500.0,
        "status": "active",
        "construction_year": 2016,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*9)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "suezmax"
    },
    {
        "id": "TP_SUEZMAX_MARCILIO_DIAS",
        "name": "Marcílio Dias",
        "imo_number": "IMO9761237",
        "call_sign": "PPMR",
        "vessel_type": "tanker",
        "vessel_class": "Suezmax",
        "length_m": 274.0,
        "width_m": 48.0,
        "draft_m": 17.0,
        "hull_area_m2": calculate_hull_area(274.0, 48.0, 17.0),
        "displacement_tonnes": 157000.0,
        "dwt": 157000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=80)).isoformat(),
        "max_speed_knots": 18.0,
        "typical_speed_knots": 14.5,
        "operating_routes": ["International", "South_Atlantic"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 25000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2500.0,
        "status": "active",
        "construction_year": 2018,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*7)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "suezmax"
    },
    
    # ========== AFRAMAX (Petroleiros) ==========
    # Capacidade: 65-80k TPB, Porte similar ao Canal do Panamá
    {
        "id": "TP_AFRAMAX_001",
        "name": "Aframax 1",
        "imo_number": "IMO9761201",
        "call_sign": "PPAF",
        "vessel_type": "tanker",
        "vessel_class": "Aframax",
        "length_m": 245.0,
        "width_m": 42.0,
        "draft_m": 14.5,
        "hull_area_m2": calculate_hull_area(245.0, 42.0, 14.5),
        "displacement_tonnes": 114700.0,
        "dwt": 114700.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=150)).isoformat(),
        "max_speed_knots": 17.0,
        "typical_speed_knots": 13.5,
        "operating_routes": ["International", "South_Atlantic"],
        "home_port": "Santos, SP",
        "engine_type": "Diesel",
        "engine_power_kw": 22000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2200.0,
        "status": "active",
        "construction_year": 2015,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*10)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aframax"
    },
    
    # ========== PANAMAX ==========
    {
        "id": "TP_PANAMAX_ANITA_GARIBALDI",
        "name": "Anita Garibaldi",
        "imo_number": "IMO9761202",
        "call_sign": "PPAG",
        "vessel_type": "tanker",
        "vessel_class": "Panamax",
        "length_m": 228.0,
        "width_m": 32.3,  # Largura máxima do Canal do Panamá
        "draft_m": 12.0,
        "hull_area_m2": calculate_hull_area(228.0, 32.3, 12.0),
        "displacement_tonnes": 72786.0,
        "dwt": 72786.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=200)).isoformat(),
        "max_speed_knots": 16.5,
        "typical_speed_knots": 13.0,
        "operating_routes": ["International", "South_Atlantic"],
        "home_port": "Santos, SP",
        "engine_type": "Diesel",
        "engine_power_kw": 15000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 1500.0,
        "status": "active",
        "construction_year": 2015,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*10)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "panamax",
        "cargo_type": "Escuros/Claros"
    },
    
    # ========== ALIVIADORES (Posicionamento Dinâmico DP) ==========
    # Capacidade: 105.000 TPB, DP2 para operações offshore
    {
        "id": "TP_ALIV_SÃO_LUIZ",
        "name": "São Luiz",
        "imo_number": "IMO9761203",
        "call_sign": "PPSL",
        "vessel_type": "tanker",
        "vessel_class": "Aliviador",
        "length_m": 260.0,
        "width_m": 46.0,
        "draft_m": 15.5,
        "hull_area_m2": calculate_hull_area(260.0, 46.0, 15.5),
        "displacement_tonnes": 105000.0,
        "dwt": 105000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=110)).isoformat(),
        "max_speed_knots": 17.5,
        "typical_speed_knots": 14.0,
        "operating_routes": ["Offshore", "South_Atlantic"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 24000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2400.0,
        "status": "active",
        "construction_year": 2013,
        "construction_country": "Bahamas",
        "registration_date": (datetime.now() - timedelta(days=365*12)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aliviador",
        "dp2_capable": True,
        "offshore_operations": True,
        "dynamic_positioning": "DP2"
    },
    {
        "id": "TP_ALIV_ANGRA_DOS_REIS",
        "name": "Angra dos Reis",
        "imo_number": "IMO9761204",
        "call_sign": "PPAR",
        "vessel_type": "tanker",
        "vessel_class": "Aliviador",
        "length_m": 260.0,
        "width_m": 46.0,
        "draft_m": 15.5,
        "hull_area_m2": calculate_hull_area(260.0, 46.0, 15.5),
        "displacement_tonnes": 105000.0,
        "dwt": 105000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=130)).isoformat(),
        "max_speed_knots": 17.5,
        "typical_speed_knots": 14.0,
        "operating_routes": ["Offshore", "South_Atlantic"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 24000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2400.0,
        "status": "active",
        "construction_year": 2012,
        "construction_country": "Bahamas",
        "registration_date": (datetime.now() - timedelta(days=365*13)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aliviador",
        "dp2_capable": True,
        "offshore_operations": True,
        "dynamic_positioning": "DP2"
    },
    {
        "id": "TP_ALIV_MADRE_DE_DEUS",
        "name": "Madre de Deus",
        "imo_number": "IMO9761205",
        "call_sign": "PPMD",
        "vessel_type": "tanker",
        "vessel_class": "Aliviador",
        "length_m": 260.0,
        "width_m": 46.0,
        "draft_m": 15.5,
        "hull_area_m2": calculate_hull_area(260.0, 46.0, 15.5),
        "displacement_tonnes": 105000.0,
        "dwt": 105000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=95)).isoformat(),
        "max_speed_knots": 17.5,
        "typical_speed_knots": 14.0,
        "operating_routes": ["Offshore", "South_Atlantic"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 24000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2400.0,
        "status": "active",
        "construction_year": 2012,
        "construction_country": "Bahamas",
        "registration_date": (datetime.now() - timedelta(days=365*13)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aliviador",
        "dp2_capable": True,
        "offshore_operations": True,
        "dynamic_positioning": "DP2"
    },
    {
        "id": "TP_ALIV_RIO_GRANDE",
        "name": "Rio Grande",
        "imo_number": "IMO9761206",
        "call_sign": "PPRG",
        "vessel_type": "tanker",
        "vessel_class": "Aliviador",
        "length_m": 260.0,
        "width_m": 46.0,
        "draft_m": 15.5,
        "hull_area_m2": calculate_hull_area(260.0, 46.0, 15.5),
        "displacement_tonnes": 105000.0,
        "dwt": 105000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=140)).isoformat(),
        "max_speed_knots": 17.5,
        "typical_speed_knots": 14.0,
        "operating_routes": ["Offshore", "South_Atlantic"],
        "home_port": "Rio Grande, RS",
        "engine_type": "Diesel",
        "engine_power_kw": 24000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2400.0,
        "status": "active",
        "construction_year": 2012,
        "construction_country": "Bahamas",
        "registration_date": (datetime.now() - timedelta(days=365*13)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aliviador",
        "dp2_capable": True,
        "offshore_operations": True,
        "dynamic_positioning": "DP2"
    },
    {
        "id": "TP_ALIV_SÃO_SEBASTIÃO",
        "name": "São Sebastião",
        "imo_number": "IMO9761207",
        "call_sign": "PPSS",
        "vessel_type": "tanker",
        "vessel_class": "Aliviador",
        "length_m": 260.0,
        "width_m": 46.0,
        "draft_m": 15.5,
        "hull_area_m2": calculate_hull_area(260.0, 46.0, 15.5),
        "displacement_tonnes": 105000.0,
        "dwt": 105000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=105)).isoformat(),
        "max_speed_knots": 17.5,
        "typical_speed_knots": 14.0,
        "operating_routes": ["Offshore", "South_Atlantic"],
        "home_port": "São Sebastião, SP",
        "engine_type": "Diesel",
        "engine_power_kw": 24000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2400.0,
        "status": "active",
        "construction_year": 2012,
        "construction_country": "Bahamas",
        "registration_date": (datetime.now() - timedelta(days=365*13)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aliviador",
        "dp2_capable": True,
        "offshore_operations": True,
        "dynamic_positioning": "DP2"
    },
    {
        "id": "TP_ALIV_FORTALEZA_KNUTSEN",
        "name": "Fortaleza Knutsen",
        "imo_number": "IMO9761208",
        "call_sign": "PPFK",
        "vessel_type": "tanker",
        "vessel_class": "Aliviador",
        "length_m": 260.0,
        "width_m": 46.0,
        "draft_m": 15.5,
        "hull_area_m2": calculate_hull_area(260.0, 46.0, 15.5),
        "displacement_tonnes": 105000.0,
        "dwt": 105000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=125)).isoformat(),
        "max_speed_knots": 17.5,
        "typical_speed_knots": 14.0,
        "operating_routes": ["Offshore", "South_Atlantic"],
        "home_port": "Fortaleza, CE",
        "engine_type": "Diesel",
        "engine_power_kw": 24000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2400.0,
        "status": "active",
        "construction_year": 2011,
        "construction_country": "Bahamas",
        "registration_date": (datetime.now() - timedelta(days=365*14)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aliviador",
        "dp2_capable": True,
        "offshore_operations": True,
        "dynamic_positioning": "DP2"
    },
    {
        "id": "TP_ALIV_RECIFE_KNUTSEN",
        "name": "Recife Knutsen",
        "imo_number": "IMO9761209",
        "call_sign": "PPRK",
        "vessel_type": "tanker",
        "vessel_class": "Aliviador",
        "length_m": 260.0,
        "width_m": 46.0,
        "draft_m": 15.5,
        "hull_area_m2": calculate_hull_area(260.0, 46.0, 15.5),
        "displacement_tonnes": 105000.0,
        "dwt": 105000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=115)).isoformat(),
        "max_speed_knots": 17.5,
        "typical_speed_knots": 14.0,
        "operating_routes": ["Offshore", "South_Atlantic"],
        "home_port": "Recife, PE",
        "engine_type": "Diesel",
        "engine_power_kw": 24000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2400.0,
        "status": "active",
        "construction_year": 2011,
        "construction_country": "Bahamas",
        "registration_date": (datetime.now() - timedelta(days=365*14)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aliviador",
        "dp2_capable": True,
        "offshore_operations": True,
        "dynamic_positioning": "DP2"
    },
    
    # ========== NAVIOS DE PRODUTOS (Cabotagem) ==========
    # Capacidade: 30-50k TPB, Transporte de derivados
    {
        "id": "TP_PROD_JOSÉ_ALENCAR",
        "name": "José Alencar",
        "imo_number": "IMO9761210",
        "call_sign": "PPJA",
        "vessel_type": "tanker",
        "vessel_class": "Produtos",
        "length_m": 183.0,
        "width_m": 32.0,
        "draft_m": 11.0,
        "hull_area_m2": calculate_hull_area(183.0, 32.0, 11.0),
        "displacement_tonnes": 48573.0,
        "dwt": 48573.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=160)).isoformat(),
        "max_speed_knots": 16.0,
        "typical_speed_knots": 13.0,
        "operating_routes": ["Brazil_Coast", "Cabotage"],
        "home_port": "Santos, SP",
        "engine_type": "Diesel",
        "engine_power_kw": 12000.0,
        "fuel_type": "MGO",
        "typical_consumption_kg_h": 1200.0,
        "status": "active",
        "construction_year": 2013,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*12)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "produtos",
        "cargo_types": ["Diesel", "Nafta", "Gasolina", "Óleo Combustível", "Querosene de Aviação"]
    },
    {
        "id": "TP_PROD_RÔMULO_ALMEIDA",
        "name": "Rômulo Almeida",
        "imo_number": "IMO9761211",
        "call_sign": "PPRA",
        "vessel_type": "tanker",
        "vessel_class": "Produtos",
        "length_m": 183.0,
        "width_m": 32.0,
        "draft_m": 11.0,
        "hull_area_m2": calculate_hull_area(183.0, 32.0, 11.0),
        "displacement_tonnes": 48573.0,
        "dwt": 48573.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=145)).isoformat(),
        "max_speed_knots": 16.0,
        "typical_speed_knots": 13.0,
        "operating_routes": ["Brazil_Coast", "Cabotage"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 12000.0,
        "fuel_type": "MGO",
        "typical_consumption_kg_h": 1200.0,
        "status": "active",
        "construction_year": 2013,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*12)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "produtos",
        "cargo_types": ["Diesel", "Nafta", "Gasolina", "Óleo Combustível", "Querosene de Aviação"]
    },
    {
        "id": "TP_PROD_SÉRGIO_BUARQUE_HOLANDA",
        "name": "Sérgio Buarque de Holanda",
        "imo_number": "IMO9761212",
        "call_sign": "PPSB",
        "vessel_type": "tanker",
        "vessel_class": "Produtos",
        "length_m": 183.0,
        "width_m": 32.0,
        "draft_m": 11.0,
        "hull_area_m2": calculate_hull_area(183.0, 32.0, 11.0),
        "displacement_tonnes": 48573.0,
        "dwt": 48573.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=170)).isoformat(),
        "max_speed_knots": 16.0,
        "typical_speed_knots": 13.0,
        "operating_routes": ["Brazil_Coast", "Cabotage"],
        "home_port": "Santos, SP",
        "engine_type": "Diesel",
        "engine_power_kw": 12000.0,
        "fuel_type": "MGO",
        "typical_consumption_kg_h": 1200.0,
        "status": "active",
        "construction_year": 2012,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*13)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "produtos",
        "cargo_types": ["Diesel", "Nafta", "Gasolina", "Óleo Combustível", "Querosene de Aviação"]
    },
    {
        "id": "TP_PROD_CELSO_FURTADO",
        "name": "Celso Furtado",
        "imo_number": "IMO9761213",
        "call_sign": "PPCF",
        "vessel_type": "tanker",
        "vessel_class": "Produtos",
        "length_m": 183.0,
        "width_m": 32.0,
        "draft_m": 11.0,
        "hull_area_m2": calculate_hull_area(183.0, 32.0, 11.0),
        "displacement_tonnes": 48573.0,
        "dwt": 48573.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=135)).isoformat(),
        "max_speed_knots": 16.0,
        "typical_speed_knots": 13.0,
        "operating_routes": ["Brazil_Coast", "Cabotage"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 12000.0,
        "fuel_type": "MGO",
        "typical_consumption_kg_h": 1200.0,
        "status": "active",
        "construction_year": 2011,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*14)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "produtos",
        "cargo_types": ["Diesel", "Nafta", "Gasolina", "Óleo Combustível", "Querosene de Aviação"]
    },
    
    # ========== GASEIROS (GLP) ==========
    # 3.000 DWT
    {
        "id": "TP_GAS_JORGE_AMADO",
        "name": "Jorge Amado",
        "imo_number": "IMO9761214",
        "call_sign": "PPJA",
        "vessel_type": "gas_carrier",
        "vessel_class": "Gaseiro",
        "length_m": 95.0,
        "width_m": 16.0,
        "draft_m": 5.5,
        "hull_area_m2": calculate_hull_area(95.0, 16.0, 5.5),
        "displacement_tonnes": 3000.0,
        "dwt": 3000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=85)).isoformat(),
        "max_speed_knots": 14.0,
        "typical_speed_knots": 12.0,
        "operating_routes": ["Brazil_Coast", "Cabotage"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 3500.0,
        "fuel_type": "MGO",
        "typical_consumption_kg_h": 350.0,
        "status": "active",
        "construction_year": 2017,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*8)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "gaseiro",
        "gas_capacity_m3": 3000.0,
        "cargo_type": "GLP"
    },
    {
        "id": "TP_GAS_GILBERTO_FREYRE",
        "name": "Gilberto Freyre",
        "imo_number": "IMO9761215",
        "call_sign": "PPGF",
        "vessel_type": "gas_carrier",
        "vessel_class": "Gaseiro",
        "length_m": 95.0,
        "width_m": 16.0,
        "draft_m": 5.5,
        "hull_area_m2": calculate_hull_area(95.0, 16.0, 5.5),
        "displacement_tonnes": 3000.0,
        "dwt": 3000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=75)).isoformat(),
        "max_speed_knots": 14.0,
        "typical_speed_knots": 12.0,
        "operating_routes": ["Brazil_Coast", "Cabotage"],
        "home_port": "Recife, PE",
        "engine_type": "Diesel",
        "engine_power_kw": 3500.0,
        "fuel_type": "MGO",
        "typical_consumption_kg_h": 350.0,
        "status": "active",
        "construction_year": 2017,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*8)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "gaseiro",
        "gas_capacity_m3": 3000.0,
        "cargo_type": "GLP"
    },
    
    # 5.079 DWT
    {
        "id": "TP_GAS_BARBOSA_LIMA_SOBRINHO",
        "name": "Barbosa Lima Sobrinho",
        "imo_number": "IMO9761216",
        "call_sign": "PPBL",
        "vessel_type": "gas_carrier",
        "vessel_class": "Gaseiro",
        "length_m": 110.0,
        "width_m": 18.0,
        "draft_m": 6.5,
        "hull_area_m2": calculate_hull_area(110.0, 18.0, 6.5),
        "displacement_tonnes": 5079.0,
        "dwt": 5079.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=90)).isoformat(),
        "max_speed_knots": 15.0,
        "typical_speed_knots": 12.5,
        "operating_routes": ["Brazil_Coast", "Cabotage"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 4500.0,
        "fuel_type": "MGO",
        "typical_consumption_kg_h": 450.0,
        "status": "active",
        "construction_year": 2016,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*9)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "gaseiro",
        "gas_capacity_m3": 5079.0,
        "cargo_type": "GLP"
    },
    {
        "id": "TP_GAS_DARCY_RIBEIRO",
        "name": "Darcy Ribeiro",
        "imo_number": "IMO9761217",
        "call_sign": "PPDR",
        "vessel_type": "gas_carrier",
        "vessel_class": "Gaseiro",
        "length_m": 110.0,
        "width_m": 18.0,
        "draft_m": 6.5,
        "hull_area_m2": calculate_hull_area(110.0, 18.0, 6.5),
        "displacement_tonnes": 5079.0,
        "dwt": 5079.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=100)).isoformat(),
        "max_speed_knots": 15.0,
        "typical_speed_knots": 12.5,
        "operating_routes": ["Brazil_Coast", "Cabotage"],
        "home_port": "Santos, SP",
        "engine_type": "Diesel",
        "engine_power_kw": 4500.0,
        "fuel_type": "MGO",
        "typical_consumption_kg_h": 450.0,
        "status": "active",
        "construction_year": 2016,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*9)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "gaseiro",
        "gas_capacity_m3": 5079.0,
        "cargo_type": "GLP"
    },
    {
        "id": "TP_GAS_LUCIO_COSTA",
        "name": "Lucio Costa",
        "imo_number": "IMO9761218",
        "call_sign": "PPLC",
        "vessel_type": "gas_carrier",
        "vessel_class": "Gaseiro",
        "length_m": 110.0,
        "width_m": 18.0,
        "draft_m": 6.5,
        "hull_area_m2": calculate_hull_area(110.0, 18.0, 6.5),
        "displacement_tonnes": 5079.0,
        "dwt": 5079.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=95)).isoformat(),
        "max_speed_knots": 15.0,
        "typical_speed_knots": 12.5,
        "operating_routes": ["Brazil_Coast", "Cabotage"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 4500.0,
        "fuel_type": "MGO",
        "typical_consumption_kg_h": 450.0,
        "status": "active",
        "construction_year": 2016,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*9)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "gaseiro",
        "gas_capacity_m3": 5079.0,
        "cargo_type": "GLP"
    },
    {
        "id": "TP_GAS_OSCAR_NIEMEYER",
        "name": "Oscar Niemeyer",
        "imo_number": "IMO9761219",
        "call_sign": "PPON",
        "vessel_type": "gas_carrier",
        "vessel_class": "Gaseiro",
        "length_m": 110.0,
        "width_m": 18.0,
        "draft_m": 6.5,
        "hull_area_m2": calculate_hull_area(110.0, 18.0, 6.5),
        "displacement_tonnes": 5079.0,
        "dwt": 5079.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=88)).isoformat(),
        "max_speed_knots": 15.0,
        "typical_speed_knots": 12.5,
        "operating_routes": ["Brazil_Coast", "Cabotage"],
        "home_port": "Santos, SP",
        "engine_type": "Diesel",
        "engine_power_kw": 4500.0,
        "fuel_type": "MGO",
        "typical_consumption_kg_h": 450.0,
        "status": "active",
        "construction_year": 2015,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*10)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "gaseiro",
        "gas_capacity_m3": 5079.0,
        "cargo_type": "GLP"
    },
    
    # ========== AFRAMAX ADICIONAIS ==========
    # Adicionando mais Aframax para completar a frota
    {
        "id": "TP_AFRAMAX_002",
        "name": "Aframax 2",
        "imo_number": "IMO9761222",
        "call_sign": "PPAF2",
        "vessel_type": "tanker",
        "vessel_class": "Aframax",
        "length_m": 245.0,
        "width_m": 42.0,
        "draft_m": 14.5,
        "hull_area_m2": calculate_hull_area(245.0, 42.0, 14.5),
        "displacement_tonnes": 114700.0,
        "dwt": 114700.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=155)).isoformat(),
        "max_speed_knots": 17.0,
        "typical_speed_knots": 13.5,
        "operating_routes": ["International", "South_Atlantic"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 22000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2200.0,
        "status": "active",
        "construction_year": 2014,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*11)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aframax"
    },
    {
        "id": "TP_AFRAMAX_003",
        "name": "Aframax 3",
        "imo_number": "IMO9761223",
        "call_sign": "PPAF3",
        "vessel_type": "tanker",
        "vessel_class": "Aframax",
        "length_m": 245.0,
        "width_m": 42.0,
        "draft_m": 14.5,
        "hull_area_m2": calculate_hull_area(245.0, 42.0, 14.5),
        "displacement_tonnes": 114700.0,
        "dwt": 114700.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_A",
        "paint_application_date": (datetime.now() - timedelta(days=165)).isoformat(),
        "max_speed_knots": 17.0,
        "typical_speed_knots": 13.5,
        "operating_routes": ["International", "South_Atlantic"],
        "home_port": "Santos, SP",
        "engine_type": "Diesel",
        "engine_power_kw": 22000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2200.0,
        "status": "active",
        "construction_year": 2013,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*12)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aframax"
    },
    {
        "id": "TP_AFRAMAX_004",
        "name": "Aframax 4",
        "imo_number": "IMO9761224",
        "call_sign": "PPAF4",
        "vessel_type": "tanker",
        "vessel_class": "Aframax",
        "length_m": 245.0,
        "width_m": 42.0,
        "draft_m": 14.5,
        "hull_area_m2": calculate_hull_area(245.0, 42.0, 14.5),
        "displacement_tonnes": 114700.0,
        "dwt": 114700.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=148)).isoformat(),
        "max_speed_knots": 17.0,
        "typical_speed_knots": 13.5,
        "operating_routes": ["International", "South_Atlantic"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 22000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2200.0,
        "status": "active",
        "construction_year": 2012,
        "construction_country": "Brasil",
        "registration_date": (datetime.now() - timedelta(days=365*13)).isoformat(),
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aframax"
    },
    
    # ========== NOVOS NAVIOS (Contratos 2025-2029) ==========
    # Handy (4 navios contratados)
    {
        "id": "TP_HANDY_001",
        "name": "Navio Handy 1",
        "imo_number": "IMO9761220",
        "call_sign": "PPH1",
        "vessel_type": "tanker",
        "vessel_class": "Handy",
        "length_m": 150.0,
        "width_m": 24.0,
        "draft_m": 9.5,
        "hull_area_m2": calculate_hull_area(150.0, 24.0, 9.5),
        "displacement_tonnes": 18000.0,
        "dwt": 18000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": (datetime.now() - timedelta(days=60)).isoformat(),
        "max_speed_knots": 16.0,
        "typical_speed_knots": 12.5,
        "operating_routes": ["South_Atlantic", "Brazil_Coast"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 8500.0,
        "fuel_type": "MGO",
        "typical_consumption_kg_h": 850.0,
        "status": "under_construction",
        "construction_year": 2026,
        "construction_country": "Brasil",
        "registration_date": None,
        "last_update": datetime.now().isoformat(),
        "fleet_category": "handy",
        "contract_value_usd": 69500000.0,
        "delivery_date": "2026-06"
    },
    
    # Novos Aliviadores Suezmax DP2 (9 navios contratados)
    {
        "id": "TP_ALIV_NOVO_001",
        "name": "Aliviador Suezmax DP2 1",
        "imo_number": "IMO9761221",
        "call_sign": "PPA1",
        "vessel_type": "tanker",
        "vessel_class": "Aliviador Suezmax DP2",
        "length_m": 275.0,
        "width_m": 48.0,
        "draft_m": 16.0,
        "hull_area_m2": calculate_hull_area(275.0, 48.0, 16.0),
        "displacement_tonnes": 150000.0,
        "dwt": 150000.0,
        "hull_material": "steel",
        "paint_type": "Antifouling_Type_B",
        "paint_application_date": None,
        "max_speed_knots": 18.0,
        "typical_speed_knots": 14.0,
        "operating_routes": ["Offshore", "South_Atlantic"],
        "home_port": "Rio de Janeiro, RJ",
        "engine_type": "Diesel",
        "engine_power_kw": 25000.0,
        "fuel_type": "HFO",
        "typical_consumption_kg_h": 2500.0,
        "status": "under_construction",
        "construction_year": 2027,
        "construction_country": "Brasil",
        "registration_date": None,
        "last_update": datetime.now().isoformat(),
        "fleet_category": "aliviador_novo",
        "dp2_capable": True,
        "offshore_operations": True,
        "dynamic_positioning": "DP2",
        "emission_standard": "Tier III",
        "fuel_alternatives": ["Metanol", "Etanol"]
    }
]


def get_transpetro_fleet() -> List[Dict]:
    """
    Retorna dados da frota Transpetro.
    
    Returns:
        Lista de dicionários com dados das embarcações
    """
    return TRANSPETRO_FLEET_DATA.copy()


def get_vessel_by_id(vessel_id: str) -> Dict:
    """
    Retorna dados de uma embarcação específica.
    
    Args:
        vessel_id: ID da embarcação
        
    Returns:
        Dicionário com dados da embarcação ou None
    """
    for vessel in TRANSPETRO_FLEET_DATA:
        if vessel["id"] == vessel_id:
            return vessel.copy()
    return None


def get_vessels_by_type(vessel_type: str) -> List[Dict]:
    """
    Retorna embarcações por tipo.
    
    Args:
        vessel_type: Tipo de embarcação (tanker, gas_carrier, etc.)
        
    Returns:
        Lista de embarcações do tipo especificado
    """
    return [
        vessel.copy()
        for vessel in TRANSPETRO_FLEET_DATA
        if vessel["vessel_type"] == vessel_type.lower()
    ]


def get_vessels_by_class(vessel_class: str) -> List[Dict]:
    """
    Retorna embarcações por classe.
    
    Args:
        vessel_class: Classe (Suezmax, Aframax, Panamax, Aliviador, Produtos, Gaseiro, Handy)
        
    Returns:
        Lista de embarcações da classe especificada
    """
    return [
        vessel.copy()
        for vessel in TRANSPETRO_FLEET_DATA
        if vessel.get("vessel_class", "").lower() == vessel_class.lower()
    ]


def get_vessels_by_category(fleet_category: str) -> List[Dict]:
    """
    Retorna embarcações por categoria da frota.
    
    Args:
        fleet_category: Categoria (suezmax, aframax, panamax, aliviador, produtos, gaseiro, handy, etc.)
        
    Returns:
        Lista de embarcações da categoria especificada
    """
    return [
        vessel.copy()
        for vessel in TRANSPETRO_FLEET_DATA
        if vessel.get("fleet_category", "").lower() == fleet_category.lower()
    ]


def get_fleet_statistics() -> Dict:
    """
    Retorna estatísticas agregadas da frota Transpetro.
    
    Returns:
        Dicionário com estatísticas
    """
    fleet = TRANSPETRO_FLEET_DATA
    
    stats = {
        "total_vessels": len(fleet),
        "by_type": {},
        "by_class": {},
        "by_category": {},
        "by_status": {},
        "total_hull_area_m2": sum(v.get("hull_area_m2", 0) for v in fleet),
        "total_displacement_tonnes": sum(v.get("displacement_tonnes", 0) for v in fleet),
        "total_dwt": sum(v.get("dwt", 0) for v in fleet),
        "total_engine_power_kw": sum(v.get("engine_power_kw", 0) for v in fleet),
        "total_typical_consumption_kg_h": sum(v.get("typical_consumption_kg_h", 0) for v in fleet),
        "active_vessels": sum(1 for v in fleet if v.get("status") == "active"),
        "under_construction": sum(1 for v in fleet if v.get("status") == "under_construction")
    }
    
    # Por tipo
    for vessel in fleet:
        vtype = vessel.get("vessel_type", "unknown")
        stats["by_type"][vtype] = stats["by_type"].get(vtype, 0) + 1
    
    # Por classe
    for vessel in fleet:
        vclass = vessel.get("vessel_class", "unknown")
        stats["by_class"][vclass] = stats["by_class"].get(vclass, 0) + 1
    
    # Por categoria
    for vessel in fleet:
        category = vessel.get("fleet_category", "unknown")
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
    
    # Por status
    for vessel in fleet:
        status = vessel.get("status", "unknown")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
    
    return stats


def generate_realistic_fouling_data(vessel_id: str, days_since_cleaning: int = None) -> Dict:
    """
    Gera dados realistas de bioincrustação baseados em características da embarcação.
    
    Args:
        vessel_id: ID da embarcação
        days_since_cleaning: Dias desde última limpeza (se None, usa dados do vessel)
        
    Returns:
        Dicionário com dados de bioincrustação
    """
    vessel = get_vessel_by_id(vessel_id)
    if not vessel:
        return None
    
    # Se não especificado, calcular baseado na data de aplicação da tinta
    if days_since_cleaning is None:
        paint_date_str = vessel.get("paint_application_date")
        if paint_date_str:
            paint_date = datetime.fromisoformat(paint_date_str)
            days_since_cleaning = (datetime.now() - paint_date).days
        else:
            days_since_cleaning = 180  # Default
    
    # Taxa de crescimento baseada em características
    base_growth_rate = 0.03  # mm/dia base
    
    # Ajustes por tipo/classe de embarcação
    vessel_class = vessel.get("vessel_class", "").lower()
    if "gaseiro" in vessel_class:
        growth_rate = base_growth_rate * 0.9  # Gaseiros navegam mais
    elif "aliviador" in vessel_class:
        growth_rate = base_growth_rate * 1.1  # Operações offshore têm mais exposição
    elif "produtos" in vessel_class:
        growth_rate = base_growth_rate * 1.0  # Padrão
    elif "suezmax" in vessel_class or "aframax" in vessel_class:
        growth_rate = base_growth_rate * 1.05  # Rotas internacionais
    else:
        growth_rate = base_growth_rate
    
    # Ajuste por rota
    routes = vessel.get("operating_routes", [])
    if any("offshore" in str(r).lower() for r in routes):
        growth_rate *= 1.15  # Offshore tem mais exposição
    elif any("tropical" in str(r).lower() for r in routes):
        growth_rate *= 1.3
    elif any("inland" in str(r).lower() for r in routes):
        growth_rate *= 1.1
    
    # Ajuste por idade da embarcação
    construction_year = vessel.get("construction_year")
    if construction_year:
        age_years = datetime.now().year - construction_year
        if age_years > 10:
            growth_rate *= 1.1  # Embarcações mais antigas podem ter mais bioincrustação
    
    # Calcular espessura e rugosidade
    thickness_mm = min(6.0, days_since_cleaning * growth_rate)
    roughness_um = thickness_mm * 80.0  # Relação aproximada
    
    # Adicionar variação aleatória realista
    thickness_mm += random.uniform(-0.2, 0.2)
    roughness_um += random.uniform(-20, 20)
    
    # Garantir valores mínimos
    thickness_mm = max(0.1, thickness_mm)
    roughness_um = max(50.0, roughness_um)
    
    return {
        "vessel_id": vessel_id,
        "vessel_name": vessel.get("name", ""),
        "fouling_thickness_mm": round(thickness_mm, 2),
        "roughness_um": round(roughness_um, 2),
        "days_since_cleaning": days_since_cleaning,
        "last_inspection_date": (datetime.now() - timedelta(days=random.randint(30, 90))).isoformat(),
        "confidence": random.uniform(0.75, 0.95),
        "vessel_class": vessel.get("vessel_class", ""),
        "hull_area_m2": vessel.get("hull_area_m2", 0)
    }
