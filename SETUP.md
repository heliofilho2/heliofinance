# 🚀 Setup - Sistema de Gestão Financeira

## 📋 Pré-requisitos

- Python 3.11+
- Conta no Telegram (para criar bot)

## 🔧 Instalação

### 1. Criar ambiente virtual

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements_api.txt
```

### 3. Configurar Bot Telegram

1. Abra o Telegram e procure por `@BotFather`
2. Envie `/newbot` e siga as instruções
3. Copie o token recebido
4. Configure variável de ambiente:

**Windows PowerShell:**
```powershell
$env:TELEGRAM_BOT_TOKEN="seu_token_aqui"
```

**Windows CMD:**
```cmd
set TELEGRAM_BOT_TOKEN=seu_token_aqui
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="seu_token_aqui"
```

### 4. Configurar URL da API (opcional)

Se a API estiver em outro servidor:

```bash
export API_URL="http://localhost:8000"
```

## ▶️ Execução

### Opção 1: Scripts Batch (Windows)

**Terminal 1 - API:**
```bash
run_api.bat
```

**Terminal 2 - Bot:**
```bash
run_bot.bat
```

### Opção 2: Comandos Manuais

**Terminal 1 - API:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Bot:**
```bash
python bot/telegram_bot.py
```

## ✅ Verificar Funcionamento

### API

Acesse: http://localhost:8000

- Health check: http://localhost:8000/health
- Dashboard: http://localhost:8000/api/dashboard
- Docs: http://localhost:8000/docs

### Bot

1. Abra o Telegram
2. Procure pelo seu bot (nome que você deu ao @BotFather)
3. Envie `/start`
4. Teste: `mercado 87`

## 📱 Endpoints da API

### Dashboard
```
GET /api/dashboard
```

### Transações
```
POST /api/transactions
GET /api/transactions?start_date=2026-01-01&end_date=2026-01-31
POST /api/transactions/quick?command=mercado 87
DELETE /api/transactions/{id}
```

### Simulações
```
POST /api/simulate/loan
POST /api/simulate/installment
POST /api/simulate/{id}/confirm
DELETE /api/simulate/{id}
```

## 🤖 Comandos do Bot

### Comandos do Sistema
- `/start` - Iniciar bot
- `/help` - Ajuda
- `/resumo` - Ver resumo financeiro
- `/confirmar <id>` - Confirmar simulação

### Registro Rápido
- `mercado 87` - Gasto variável
- `recebi cliente 2500` - Receita
- `aluguel 1200` - Gasto fixo
- `simular emprestimo 10000 18 0.02` - Simular empréstimo
- `simular compra notebook 4200 10` - Simular compra parcelada

## 🗄️ Banco de Dados

O banco SQLite é criado automaticamente em `data/finance.db` na primeira execução.

## 🔒 Segurança

**IMPORTANTE:** Este sistema é para uso pessoal. Não inclui:
- Autenticação complexa
- Multiusuário
- Criptografia de dados

Para uso em produção, adicione autenticação adequada.

## 🐛 Troubleshooting

### Bot não responde
- Verifique se `TELEGRAM_BOT_TOKEN` está configurado
- Verifique se a API está rodando
- Verifique logs do bot

### API não inicia
- Verifique se a porta 8000 está livre
- Verifique se todas as dependências foram instaladas

### Erro de importação
- Certifique-se de estar no diretório raiz do projeto
- Verifique se o ambiente virtual está ativado

## 📝 Próximos Passos

1. Testar com dados reais
2. Desenvolver app Android (Flutter) consumindo a API
3. Adicionar mais funcionalidades conforme necessário
