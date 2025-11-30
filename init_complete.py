#!/usr/bin/env python3
"""
Script de Inicialização Completa e Automática - HullZero

Este script automatiza todo o processo de inicialização:
1. Verifica/cria ambiente virtual
2. Instala dependências
3. Inicializa banco de dados (migrações, dados de referência)
4. Executa testes de integridade
5. Opcionalmente inicia backend e frontend

Uso:
    python init_complete.py [--skip-db] [--skip-tests] [--start-services]
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Cores para output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_step(message):
    """Imprime mensagem de passo"""
    print(f"{Colors.BLUE}▶ {message}{Colors.NC}")

def print_success(message):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def print_warning(message):
    """Imprime mensagem de aviso"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")

def print_error(message):
    """Imprime mensagem de erro"""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def check_python_version():
    """Verifica versão do Python"""
    print_step("Verificando versão do Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ é necessário. Versão atual: {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} OK")
    return True

def setup_virtual_environment():
    """Cria ou ativa ambiente virtual"""
    print_step("Configurando ambiente virtual...")
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print_warning("Criando ambiente virtual...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print_success("Ambiente virtual criado")
        except subprocess.CalledProcessError:
            print_error("Falha ao criar ambiente virtual")
            return False
    else:
        print_success("Ambiente virtual já existe")
    
    # Determinar caminho do executável Python no venv
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    return str(python_exe), str(pip_exe)

def install_dependencies(pip_exe):
    """Instala dependências do projeto"""
    print_step("Instalando dependências...")
    
    if not Path("requirements.txt").exists():
        print_warning("requirements.txt não encontrado, pulando instalação")
        return True
    
    try:
        # Atualizar pip primeiro
        subprocess.run([pip_exe, "install", "--upgrade", "pip", "-q"], check=True)
        
        # Instalar dependências
        subprocess.run([pip_exe, "install", "-r", "requirements.txt", "-q"], check=True)
        print_success("Dependências instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Falha ao instalar dependências: {e}")
        return False

def initialize_database(python_exe):
    """Inicializa banco de dados"""
    print_step("Inicializando banco de dados...")
    
    try:
        # 1. Criar tabelas normalizadas
        print_step("  Criando tabelas normalizadas...")
        result = subprocess.run(
            [python_exe, "-m", "src.database.create_normalized_tables"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success("  Tabelas criadas")
        else:
            print_warning(f"  Aviso ao criar tabelas: {result.stderr[:200]}")
        
        # 2. Executar migrações
        print_step("  Executando migrações...")
        result = subprocess.run(
            [python_exe, "-m", "src.database.migrate", "run"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success("  Migrações executadas")
        else:
            print_warning(f"  Aviso nas migrações: {result.stderr[:200]}")
        
        # 3. Inicializar dados de referência
        print_step("  Inicializando dados de referência...")
        result = subprocess.run(
            [python_exe, "-m", "src.database.init_reference_data"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success("  Dados de referência inicializados")
        else:
            print_warning(f"  Aviso ao inicializar dados: {result.stderr[:200]}")
        
        # 4. Migrar dados existentes
        print_step("  Migrando dados existentes...")
        result = subprocess.run(
            [python_exe, "-m", "src.database.migrate_data"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Extrair estatísticas da saída
            output = result.stdout
            if "aplicações de tinta migradas" in output:
                print_success("  Dados migrados")
            else:
                print_success("  Migração concluída (sem dados novos)")
        else:
            print_warning(f"  Aviso na migração: {result.stderr[:200]}")
        
        # 5. Inicializar autenticação e autorização
        print_step("  Inicializando autenticação e autorização...")
        result = subprocess.run(
            [python_exe, "src/auth/init_auth_data.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success("  Autenticação inicializada")
        else:
            print_warning(f"  Aviso na inicialização de auth: {result.stderr[:200]}")
        
        return True
    except Exception as e:
        print_error(f"Erro ao inicializar banco de dados: {e}")
        return False

def run_integrity_tests(python_exe):
    """Executa testes de integridade"""
    print_step("Executando testes de integridade...")
    
    try:
        result = subprocess.run(
            [python_exe, "-m", "src.database.test_integrity"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Verificar se todos os testes passaram
            if "✅ Todos os testes de integridade passaram!" in result.stdout:
                print_success("Todos os testes de integridade passaram")
                return True
            else:
                print_warning("Alguns testes falharam")
                print(result.stdout[-500:])  # Mostrar últimas linhas
                return False
        else:
            print_warning("Erro ao executar testes")
            print(result.stderr[:300])
            return False
    except Exception as e:
        print_error(f"Erro ao executar testes: {e}")
        return False

def start_services(python_exe):
    """Inicia backend e frontend"""
    print_step("Iniciando serviços...")
    
    # Verificar se já estão rodando
    import socket
    def check_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    # Iniciar backend
    if check_port(8000):
        print_warning("Backend já está rodando na porta 8000")
    else:
        print_step("  Iniciando backend...")
        if sys.platform == "win32":
            subprocess.Popen(
                [python_exe, "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                stdout=open("backend.log", "w"),
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
        else:
            subprocess.Popen(
                [python_exe, "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                stdout=open("backend.log", "w"),
                stderr=subprocess.STDOUT
            )
        print_success("  Backend iniciado (verifique backend.log)")
    
    # Iniciar frontend
    if check_port(5173):
        print_warning("Frontend já está rodando na porta 5173")
    else:
        print_step("  Iniciando frontend...")
        frontend_dir = Path("frontend")
        if frontend_dir.exists():
            if sys.platform == "win32":
                subprocess.Popen(
                    ["npm", "run", "dev"],
                    cwd=frontend_dir,
                    stdout=open("frontend.log", "w"),
                    stderr=subprocess.STDOUT,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                subprocess.Popen(
                    ["npm", "run", "dev"],
                    cwd=frontend_dir,
                    stdout=open("frontend.log", "w"),
                    stderr=subprocess.STDOUT
                )
            print_success("  Frontend iniciado (verifique frontend.log)")
        else:
            print_warning("  Diretório frontend não encontrado")
    
    print_success("Serviços iniciados")
    print(f"\n{Colors.CYAN}📍 Acesse:{Colors.NC}")
    print(f"   🖥️  Frontend:  http://localhost:5173")
    print(f"   📡 Backend:    http://localhost:8000")
    print(f"   📚 API Docs:   http://localhost:8000/docs")
    print(f"   🔍 Health:     http://localhost:8000/health")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Inicialização completa do HullZero")
    parser.add_argument("--skip-db", action="store_true", help="Pular inicialização do banco de dados")
    parser.add_argument("--skip-tests", action="store_true", help="Pular testes de integridade")
    parser.add_argument("--start-services", action="store_true", help="Iniciar backend e frontend após inicialização")
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"{Colors.CYAN}  🚀 HullZero - Inicialização Completa e Automática{Colors.NC}")
    print("=" * 60)
    print()
    
    # 1. Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # 2. Configurar ambiente virtual
    result = setup_virtual_environment()
    if not result:
        sys.exit(1)
    python_exe, pip_exe = result
    
    # 3. Instalar dependências
    if not install_dependencies(pip_exe):
        sys.exit(1)
    
    # 4. Inicializar banco de dados
    if not args.skip_db:
        if not initialize_database(python_exe):
            print_warning("Continuação apesar de erros no banco de dados")
    else:
        print_warning("Inicialização do banco de dados pulada (--skip-db)")
    
    # 5. Executar testes
    if not args.skip_tests:
        run_integrity_tests(python_exe)
    else:
        print_warning("Testes de integridade pulados (--skip-tests)")
    
    # 6. Ingerir dados reais
    print_step("Ingerindo dados reais...")
    try:
        subprocess.run([python_exe, "src/database/ingest_real_data.py"], env={**os.environ, "PYTHONPATH": "."}, check=True)
        print_success("Dados reais ingeridos")
    except subprocess.CalledProcessError:
        print_warning("Falha ao ingerir dados reais (pode ser ignorado se já existirem)")

    # 7. Gerar dados variados
    print_step("Gerando dados variados...")
    try:
        subprocess.run([python_exe, "src/database/generate_varied_data.py"], env={**os.environ, "PYTHONPATH": "."}, check=True)
        print_success("Dados variados gerados")
    except subprocess.CalledProcessError:
        print_warning("Falha ao gerar dados variados")

    # 8. Iniciar serviços (opcional)
    if args.start_services:
        start_services(python_exe)
    else:
        print(f"\n{Colors.CYAN}💡 Para iniciar os serviços, execute:{Colors.NC}")
        print(f"   python init_complete.py --start-services")
        print(f"   ou use: ./iniciar_aplicacao.sh")
    
    print()
    print("=" * 60)
    print_success("Inicialização completa!")
    print("=" * 60)

if __name__ == "__main__":
    main()

