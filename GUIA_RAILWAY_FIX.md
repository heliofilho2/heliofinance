# 🔧 Correções Aplicadas para Railway

## Problemas Identificados

1. ❌ Railway não estava detectando Python (`pip: not found`)
2. ❌ Falta de configuração para ler credenciais do Google via variável de ambiente
3. ❌ Build falhando porque não encontrava Python

## Soluções Aplicadas

### 1. Arquivos de Configuração Criados

✅ **`runtime.txt`** - Especifica versão do Python (3.12)
✅ **`railway.json`** - Configuração do Railway
✅ **`requirements_api.txt`** - Adicionado `python-dotenv`

### 2. Código Modificado

✅ **`api/api_google_sheets.py`** - Lê credenciais de `GOOGLE_CREDENTIALS`
✅ **`bot/breno_bot.py`** - Lê credenciais de `GOOGLE_CREDENTIALS`
✅ **`bot/scheduler_breno.py`** - Lê credenciais de `GOOGLE_CREDENTIALS`

## Como Configurar no Railway

### Passo 1: Variáveis de Ambiente

Para cada serviço (API, Bot, Scheduler), adicione estas variáveis:

```
PORT=8000
GOOGLE_CREDENTIALS=<cole_o_json_completo_aqui>
SPREADSHEET_ID=1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id
```

**Importante**: A variável `GOOGLE_CREDENTIALS` deve conter o JSON completo do arquivo `google-credentials.json`.

### Passo 2: Start Commands

**Serviço API:**
```
python api/api_google_sheets.py
```

**Serviço Bot:**
```
python bot/breno_bot.py
```

**Serviço Scheduler:**
```
python bot/scheduler_breno.py
```

### Passo 3: Build Command

Deixe vazio ou use:
```
pip install -r requirements_api.txt
```

O Railway deve detectar automaticamente Python pelo `runtime.txt`.

## Como Obter o JSON das Credenciais

1. Abra o arquivo `google-credentials.json` local
2. Copie TODO o conteúdo (desde `{` até `}`)
3. Cole na variável `GOOGLE_CREDENTIALS` no Railway

**Exemplo:**
```json
{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  "private_key": "...",
  ...
}
```

## Teste Após Deploy

1. **API**: Acesse `https://seu-app.railway.app/api/status`
2. **Bot**: Envie `/start` no Telegram
3. **Logs**: Verifique logs em cada serviço para erros

## Troubleshooting

### Erro: "pip: not found"
- Verifique se `runtime.txt` está na raiz
- Verifique se `requirements_api.txt` existe

### Erro: "GOOGLE_CREDENTIALS_PATH não configurado"
- Verifique se a variável `GOOGLE_CREDENTIALS` está configurada
- Verifique se o JSON está completo (sem quebras de linha extras)

### Erro: "FileNotFoundError: google-credentials.json"
- O código agora cria automaticamente a partir de `GOOGLE_CREDENTIALS`
- Verifique os logs para ver se o arquivo foi criado em `/tmp/`
