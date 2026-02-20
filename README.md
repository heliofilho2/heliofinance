# 💰 Gestão Financeira - Método Breno

Bot Telegram simplificado para gestão financeira pessoal baseado no método do Breno Nogueira, trabalhando diretamente com Google Sheets.

## 🚀 Funcionalidades

- ✅ **Registro rápido de gastos** - `/gasto` ou mensagem simples
- ✅ **Semáforo financeiro** - Visualização rápida da situação
- ✅ **Consulta rápida** - `/posso [valor]` para verificar antes de gastar
- ✅ **Integração direta com Google Sheets** - Atualiza sua planilha automaticamente
- ✅ **Lembretes automáticos** - 20h (fechamento) e 8h (resumo matinal)
- ✅ **Cálculo automático de saldo** - Propaga saldos para os dias seguintes

## 📋 Estrutura do Projeto

```
├── bot/                    # Telegram Bot
│   ├── breno_bot.py       # Bot principal simplificado
│   └── scheduler_breno.py # Agendador de lembretes
├── services/               # Serviços
│   └── google_sheets_breno.py  # Integração Google Sheets
└── requirements_api.txt    # Dependências
```

**Nota:** O projeto foi simplificado para focar apenas no Bot Telegram + Google Sheets. 
Código antigo (API, banco de dados, Flutter) foi removido para manter apenas o essencial.

## 🛠️ Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements_api.txt
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id
GOOGLE_CREDENTIALS_PATH=caminho/para/credentials.json
API_URL=http://localhost:8000
```

### 3. Inicializar Banco de Dados

O banco será criado automaticamente ao iniciar a API.

## 🚀 Como Usar

### Iniciar Bot Telegram

```bash
python bot/breno_bot.py
```

Ou use o script:
```bash
.\run_breno_bot.bat
```

### Iniciar Agendador (Lembretes Automáticos)

Em outro terminal:

```bash
python bot/scheduler_breno.py
```

Ou use o script:
```bash
.\run_scheduler_breno.bat
```

## 📱 Comandos do Bot Telegram

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `/start` | Ver comandos disponíveis | `/start` |
| `/gasto` | Registrar gasto diário | `/gasto 50 mercado` |
| `/entrada` | Registrar receita | `/entrada 2500 cliente X` |
| `/saida` | Registrar saída fixa | `/saida 1200 aluguel` |
| `/status` | Ver semáforo e saldo | `/status` |
| `/posso` | Verificar se pode gastar | `/posso 100` |

### Mensagens Simples

Você também pode enviar mensagens simples sem usar comandos:
- `mercado 50` - Registra gasto de R$ 50,00
- `recebi 2500` - Registra entrada de R$ 2.500,00
- `aluguel 1200` - Registra saída fixa de R$ 1.200,00

## 🚦 Semáforo

O semáforo indica sua situação financeira:
- 🟢 **Verde**: Saldo positivo e performance positiva
- 🟡 **Amarelo**: Atenção! Performance negativa ou gasto próximo do limite
- 🔴 **Vermelho**: Saldo negativo! Evite novos gastos

## 📊 Integração Google Sheets

O bot trabalha diretamente com sua planilha Google Sheets:

1. Configure credenciais (veja `GOOGLE_SHEETS_SETUP.md`)
2. Compartilhe a planilha com o email da service account
3. O bot atualiza automaticamente:
   - Coluna **Diário** ao usar `/gasto`
   - Coluna **Entrada** ao usar `/entrada`
   - Coluna **Saída** ao usar `/saida`
   - Coluna **Saldo** (calculado automaticamente)

## 📚 Documentação

- `README_BRENO_BOT.md` - Guia completo do bot
- `GOOGLE_SHEETS_SETUP.md` - Configuração do Google Sheets
- `SETUP.md` - Guia de configuração completo

## 🎯 Tecnologias

- **Bot:** Python 3.11+, python-telegram-bot
- **Google Sheets:** gspread, google-auth
- **Agendamento:** schedule

## 📝 Licença

Uso pessoal.

---

**Desenvolvido para gestão financeira pessoal seguindo o método do Breno Nogueira**
