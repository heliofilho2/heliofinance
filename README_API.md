# 💰 Sistema de Gestão Financeira - API + Bot Telegram

Sistema completo com backend FastAPI, bot Telegram e API REST pronta para app Android.

## 🏗️ Arquitetura

```
BRENOPLANILHA/
├── app/                    # FastAPI
│   ├── main.py            # Aplicação principal
│   └── database.py        # Configuração SQLAlchemy
│
├── core/                   # Lógica de negócio
│   ├── models_sqlalchemy.py  # Modelos SQLAlchemy
│   └── finance_engine_api.py # Motor financeiro
│
├── api/                    # Rotas REST
│   ├── routes_transactions.py
│   ├── routes_dashboard.py
│   └── routes_simulations.py
│
├── bot/                    # Bot Telegram
│   ├── telegram_bot.py
│   └── parser.py
│
└── data/                   # SQLite (criado automaticamente)
```

## 🚀 Início Rápido

### 1. Setup

```bash
# Criar venv
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements_api.txt
```

### 2. Configurar Bot Telegram

1. Abra Telegram → `@BotFather`
2. `/newbot` → siga instruções
3. Copie o token
4. Configure variável:

```bash
# Windows PowerShell
$env:TELEGRAM_BOT_TOKEN="seu_token"

# Windows CMD
set TELEGRAM_BOT_TOKEN=seu_token

# Linux/Mac
export TELEGRAM_BOT_TOKEN="seu_token"
```

### 3. Executar

**Terminal 1 - API:**
```bash
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Bot:**
```bash
python bot/telegram_bot.py
```

## 📡 Endpoints da API

### Dashboard
```
GET /api/dashboard
```

Retorna:
- Saldo atual
- Performance do mês
- Semáforo (status)
- Comprometimento
- Projeção 3 meses
- Parcelas ativas

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

## 🤖 Bot Telegram

### Comandos
- `/start` - Iniciar
- `/help` - Ajuda
- `/resumo` - Resumo financeiro
- `/confirmar <id>` - Confirmar simulação

### Registro Rápido
- `mercado 87` → Gasto variável
- `recebi cliente 2500` → Receita
- `aluguel 1200` → Gasto fixo
- `simular emprestimo 10000 18 0.02` → Simular empréstimo
- `simular compra notebook 4200 10` → Simular compra

## 📱 Para App Android (Flutter)

A API está pronta para consumo. Exemplo de chamada:

```dart
// Dashboard
final response = await http.get(
  Uri.parse('http://seu-servidor:8000/api/dashboard')
);

// Criar transação
final response = await http.post(
  Uri.parse('http://seu-servidor:8000/api/transactions/quick?command=mercado 87')
);
```

## 🔧 Configuração

### Variáveis de Ambiente

- `TELEGRAM_BOT_TOKEN` - Token do bot (obrigatório)
- `API_URL` - URL da API (padrão: http://localhost:8000)

### Banco de Dados

SQLite criado automaticamente em `data/finance.db`

## 📊 Motor Financeiro

### Performance Mensal
```
Performance = Entradas - (Fixos + Variáveis + Parcelas)
```

### Comprometimento
```
Comprometimento = (Fixos + Parcelas) / Média Receita 3 meses
```

### Semáforo
- 🟢 Verde: Performance >= 0
- 🟡 Amarelo: Performance < 0 mas acima limite crítico
- 🔴 Vermelho: Performance abaixo limite crítico

## 🎯 Características

✅ **Sem dependência de Excel** - Tudo em SQLite  
✅ **Fluxo contínuo** - Baseado em transações com data real  
✅ **Registro rápido** - Bot Telegram  
✅ **API REST** - Pronta para app  
✅ **Simulações** - Empréstimos e compras parceladas  
✅ **Projeções** - Saldo futuro automático  

## 🔒 Segurança

⚠️ **Uso pessoal apenas** - Não inclui autenticação complexa

Para produção, adicione:
- Autenticação JWT
- HTTPS
- Rate limiting
- Validação de entrada

## 📝 Documentação da API

Acesse: http://localhost:8000/docs

Interface Swagger automática com todos os endpoints.

---

**Sistema simples, claro e funcional para uso pessoal** 🎯
