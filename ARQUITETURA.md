# 🏗️ Arquitetura do Sistema

## 📁 Estrutura de Pastas

```
BRENOPLANILHA/
├── app/                    # FastAPI Application
│   ├── main.py            # Aplicação principal FastAPI
│   └── database.py        # Configuração SQLAlchemy
│
├── core/                   # Lógica de Negócio
│   ├── models_sqlalchemy.py  # Modelos SQLAlchemy
│   └── finance_engine_api.py # Motor financeiro (cálculos)
│
├── api/                    # Rotas REST
│   ├── routes_transactions.py  # CRUD de transações
│   ├── routes_dashboard.py    # Dashboard e métricas
│   └── routes_simulations.py  # Simulações
│
├── bot/                    # Bot Telegram
│   ├── telegram_bot.py    # Bot principal
│   └── parser.py          # Parser de comandos
│
└── data/                   # Banco SQLite (criado automaticamente)
    └── finance.db
```

## 🔄 Fluxo de Dados

### 1. Registro via Bot Telegram

```
Usuário → Telegram → Bot → Parser → API → Database
                              ↓
                         Resposta → Bot → Telegram → Usuário
```

### 2. Consulta via API

```
App/Cliente → HTTP Request → FastAPI → FinanceEngine → Database
                                    ↓
                              JSON Response → App/Cliente
```

## 🧩 Componentes

### Backend (FastAPI)

**app/main.py**
- Configuração FastAPI
- CORS
- Registro de rotas
- Health checks

**app/database.py**
- SQLAlchemy engine
- Session factory
- Inicialização do banco

### Core (Lógica de Negócio)

**core/models_sqlalchemy.py**
- Transaction (SQLAlchemy)
- InstallmentGroup (SQLAlchemy)
- UserSettings (SQLAlchemy)

**core/finance_engine_api.py**
- Cálculo de performance mensal
- Comprometimento
- Semáforo financeiro
- Projeções futuras
- Parcela máxima

### API (Rotas REST)

**api/routes_transactions.py**
- POST /api/transactions
- GET /api/transactions
- DELETE /api/transactions/{id}
- POST /api/transactions/quick

**api/routes_dashboard.py**
- GET /api/dashboard

**api/routes_simulations.py**
- POST /api/simulate/loan
- POST /api/simulate/installment
- POST /api/simulate/{id}/confirm
- DELETE /api/simulate/{id}

### Bot Telegram

**bot/telegram_bot.py**
- Handlers de comandos
- Processamento de mensagens
- Integração com API

**bot/parser.py**
- Parse de comandos rápidos
- Detecção de tipo (receita/despesa)
- Detecção de simulações

## 🗄️ Modelo de Dados

### Transaction
- Armazena todas as transações financeiras
- Tipos: income, fixed, variable, installment
- Relacionamento opcional com InstallmentGroup

### InstallmentGroup
- Grupos de parcelas (empréstimos/compras)
- Flag is_simulation para simulações não confirmadas
- Cálculo automático de parcelas restantes

### UserSettings
- Configurações globais
- Limites de alerta/crítico
- Médias configuradas

## 🔧 Princípios de Design

1. **Separação de Responsabilidades**
   - Core: Lógica pura
   - API: Interface HTTP
   - Bot: Interface Telegram

2. **Reutilização**
   - FinanceEngine usado por API e Bot
   - Parser usado por API e Bot

3. **Simplicidade**
   - Sem overengineering
   - Código direto e claro
   - Foco em uso pessoal

4. **Extensibilidade**
   - Fácil adicionar novos endpoints
   - Fácil adicionar novos comandos ao bot
   - Pronto para app Android

## 🚀 Fluxo de Execução

### Inicialização

1. FastAPI inicia → `app/main.py`
2. Banco inicializado → `app/database.py`
3. Tabelas criadas → SQLAlchemy Base.metadata
4. Rotas registradas → FastAPI routers

### Processamento de Transação

1. Bot recebe mensagem → `bot/telegram_bot.py`
2. Parser processa → `bot/parser.py`
3. Request HTTP → `api/routes_transactions.py`
4. Validação → Pydantic models
5. Persistência → SQLAlchemy
6. Cálculo → `core/finance_engine_api.py`
7. Resposta → JSON

## 📊 Motor Financeiro

### Cálculos Principais

**Performance Mensal:**
```python
performance = entradas - (fixos + variaveis + parcelas)
```

**Comprometimento:**
```python
ratio = (fixos + parcelas) / media_receita_3_meses * 100
```

**Semáforo:**
```python
if performance >= 0: verde
elif performance > limite_critico: amarelo
else: vermelho
```

**Projeção:**
```python
saldo_futuro = saldo_atual + Σ(performance_projetada)
```

## 🔐 Segurança

⚠️ **Uso pessoal** - Não inclui:
- Autenticação JWT
- Multiusuário
- Criptografia de dados sensíveis

Para produção, adicionar:
- Autenticação adequada
- HTTPS obrigatório
- Rate limiting
- Validação rigorosa

## 📱 Integração Futura (App Android)

A API está pronta para consumo:

```dart
// Exemplo Flutter
final response = await http.get(
  Uri.parse('http://seu-servidor:8000/api/dashboard')
);
final data = jsonDecode(response.body);
```

Todos os endpoints retornam JSON padronizado.

---

**Arquitetura simples, clara e funcional** 🎯
