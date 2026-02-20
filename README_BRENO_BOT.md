# 🤖 Bot Telegram - Método Breno

Bot simplificado para gestão financeira pessoal baseado no Método Breno, trabalhando diretamente com Google Sheets.

## 🎯 Funcionalidades

- ✅ **Registro rápido de gastos** - `/gasto` ou mensagem simples
- ✅ **Registro de entradas** - `/entrada`
- ✅ **Registro de saídas fixas** - `/saida`
- ✅ **Semáforo financeiro** - `/status`
- ✅ **Consulta rápida** - `/posso [valor]`
- ✅ **Lembretes automáticos** - 20h e 8h

## 📋 Comandos

### Comandos Principais

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

- `mercado 50` → Registra gasto de R$ 50,00
- `recebi 2500` → Registra entrada de R$ 2.500,00
- `aluguel 1200` → Registra saída fixa de R$ 1.200,00

## 🚦 Semáforo

O semáforo indica sua situação financeira:

- 🟢 **Verde**: Saldo positivo e performance positiva
- 🟡 **Amarelo**: Atenção! Performance negativa ou gasto próximo do limite
- 🔴 **Vermelho**: Saldo negativo! Evite novos gastos

## ⚙️ Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements_api.txt
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
GOOGLE_CREDENTIALS_PATH=caminho/para/credentials.json
```

### 3. Configurar Google Sheets

1. Siga o guia em `GOOGLE_SHEETS_SETUP.md`
2. Compartilhe a planilha com o email da service account
3. O ID da planilha já está configurado no código

## 🚀 Como Usar

### Iniciar Bot

```bash
python bot/breno_bot.py
```

Ou use o script:
```bash
.\run_bot.bat
```

### Iniciar Agendador (Lembretes)

Em outro terminal:

```bash
python bot/scheduler_breno.py
```

## 📊 Estrutura da Planilha

O bot trabalha com a estrutura padrão do Método Breno:

- **Data**: Dia do mês
- **Entrada**: Receitas do dia
- **Saída**: Gastos fixos do dia
- **Diário**: Gastos variáveis do dia
- **Saldo**: Saldo acumulado

O bot atualiza automaticamente:
- A coluna correspondente (Entrada, Saída ou Diário)
- O saldo do dia atual
- Os saldos dos dias seguintes (propagação automática)

## 🔔 Lembretes Automáticos

O bot envia lembretes automáticos:

- **20:00** - Lembrete de fechamento do dia
- **08:00** - Resumo matinal com limite diário sugerido

Para ativar, configure seu chat_id:
1. Envie `/start` para o bot
2. Use o comando `/setchatid` (se disponível)
3. Ou edite manualmente o arquivo `telegram_chat_id.txt`

## 💡 Dicas

1. **Registre gastos imediatamente** - Use mensagens simples como `mercado 50`
2. **Consulte antes de gastar** - Use `/posso 100` para verificar
3. **Acompanhe o semáforo** - Use `/status` regularmente
4. **Mantenha o bot rodando** - Para receber lembretes automáticos

## 🛠️ Troubleshooting

### Erro: "GOOGLE_CREDENTIALS_PATH não configurado"
- Configure a variável de ambiente `GOOGLE_CREDENTIALS_PATH`
- Ou passe o caminho no código

### Erro: "Permission denied" no Google Sheets
- Compartilhe a planilha com o email da service account
- Verifique se o email está correto no arquivo de credenciais

### Bot não responde
- Verifique se o token está correto
- Verifique se o bot está rodando
- Veja os logs no terminal

---

**Desenvolvido para facilitar o uso do Método Breno no dia a dia! 💰**
