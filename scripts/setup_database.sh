#!/bin/bash
# Script de Configuração do Banco de Dados - HullZero

echo "🚀 Configurando banco de dados HullZero..."

# Verificar se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Erro: Execute este script a partir do diretório raiz do projeto"
    exit 1
fi

# Ativar ambiente virtual (se existir)
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -q sqlalchemy psycopg2-binary

# Inicializar banco de dados
echo "🗄️  Inicializando banco de dados..."
python scripts/init_database.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Banco de dados configurado com sucesso!"
    echo ""
    echo "📊 Próximos passos:"
    echo "   1. Configure DATABASE_URL se necessário (padrão: SQLite)"
    echo "   2. Use os endpoints /api/db/* para acessar dados do banco"
    echo "   3. Consulte docs/tecnico/BANCO_DADOS.md para mais informações"
else
    echo ""
    echo "❌ Erro ao configurar banco de dados"
    exit 1
fi

