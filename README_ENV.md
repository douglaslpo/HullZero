# 🔐 Configuração de Variáveis de Ambiente - HullZero

Este projeto agora utiliza arquivos `.env` para gerenciar configurações de forma segura e organizada.

## 📋 Configuração Inicial

### 1. Criar arquivo `.env`

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

### 2. Editar `.env`

Abra o arquivo `.env` e configure as variáveis conforme necessário:

```bash
nano .env
# ou
vim .env
# ou use seu editor preferido
```

## 🔑 Variáveis Importantes

### ⚠️ **OBRIGATÓRIAS EM PRODUÇÃO**

- **`SECRET_KEY`**: Chave secreta para JWT. **DEVE ser alterada em produção!**
  - Gerar uma chave segura:
    ```bash
    python -c "import secrets; print(secrets.token_urlsafe(32))"
    ```

- **`DATABASE_URL`**: URL de conexão do banco de dados
  - Desenvolvimento: `sqlite:///./hullzero.db`
  - Produção: `postgresql://usuario:senha@localhost:5432/hullzero`

### 📝 **Configurações Recomendadas**

- **`CORS_ORIGINS`**: URLs permitidas para requisições CORS
- **`FRONTEND_URL`**: URL do frontend
- **`API_PORT`**: Porta da API (padrão: 8000)

## 🚀 Uso

### Desenvolvimento

O arquivo `.env` é carregado automaticamente quando você:

1. Inicia o backend:
   ```bash
   python -m uvicorn src.api.main:app --reload
   ```

2. Executa scripts Python:
   ```bash
   python scripts/import_real_data.py
   ```

### Produção

1. Configure as variáveis de ambiente no servidor
2. Ou use o arquivo `.env` (certifique-se de que não está no Git!)
3. O arquivo `.env` já está no `.gitignore`

## 📦 Instalação de Dependências

Certifique-se de ter `python-dotenv` instalado:

```bash
pip install -r requirements.txt
```

## 🔒 Segurança

- ✅ O arquivo `.env` está no `.gitignore`
- ✅ Use `.env.example` como template (sem valores sensíveis)
- ✅ **NUNCA** commite o arquivo `.env` no Git
- ✅ Em produção, use variáveis de ambiente do sistema ou serviços de gerenciamento de secrets

## 📚 Variáveis Disponíveis

Consulte o arquivo `.env.example` para ver todas as variáveis disponíveis e suas descrições.

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"

Instale a dependência:
```bash
pip install python-dotenv
```

### Variáveis não estão sendo carregadas

1. Verifique se o arquivo `.env` existe na raiz do projeto
2. Verifique se o arquivo tem permissões de leitura
3. Reinicie o servidor/script

### Valores padrão sendo usados

Se as variáveis não estiverem definidas, o sistema usa valores padrão seguros para desenvolvimento.

