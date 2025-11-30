# Como Rodar a Validação na Nuvem ☁️

Siga estes passos para aplicar a atualização e gerar os resultados de validação no servidor.

## 1. Upload do Arquivo
Faça o upload do arquivo `validation_update.zip` para a pasta raiz do projeto no servidor (mesma pasta onde está o `main.py`, `requirements.txt`, etc.).

## 2. Executar a Atualização
No terminal do servidor, execute os seguintes comandos:

```bash
# 1. Descompactar o arquivo
unzip -o validation_update.zip

# 2. Entrar na pasta de atualização
cd update_validation

# 3. Dar permissão de execução ao script
chmod +x apply.sh

# 4. Rodar o script
./apply.sh
```

## 3. O que vai acontecer?
1.  O script vai atualizar o código do backend (`repositories.py`).
2.  Vai rodar a geração de dados (`generate_validation.py`).
3.  Os dados serão salvos no banco de dados.
4.  Um arquivo CSV será gerado em `validacao/RESULTADO_PREENCHIDO.csv`.

## 4. (Opcional) Reiniciar a API
Para garantir que a API use a versão mais recente do código (embora os dados já apareçam sem isso), você pode reiniciar o serviço:

```bash
pm2 restart hullzero-api
```

## 5. Verificar
Acesse o dashboard da aplicação.
- Procure pelos navios "NAVIO TESTE".
- Verifique o histórico das embarcações validadas.
