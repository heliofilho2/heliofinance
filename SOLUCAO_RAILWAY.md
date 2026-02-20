# 🚨 SOLUÇÃO URGENTE: Railway não detecta Python

## Problema Identificado

O `venv/` está commitado no Git, o que está confundindo o Railway e impedindo a detecção de Python.

## Solução Imediata

Execute estes comandos:

```powershell
# 1. Remover venv do Git (mas manter localmente)
git rm -r --cached venv/

# 2. Verificar .gitignore
# Certifique-se que venv/ está no .gitignore (já está)

# 3. Commit
git add .gitignore
git commit -m "Remove venv do Git - corrige detecção Python no Railway"

# 4. Push
git push origin master
```

## Arquivos Criados para Railway

✅ **`nixpacks.toml`** - Força detecção de Python 3.12
✅ **`runtime.txt`** - Especifica versão Python
✅ **`setup.py`** - Ajuda detecção de Python
✅ **`build.sh`** - Script alternativo de build

## Após Remover venv e Fazer Push

O Railway deve:
1. ✅ Detectar Python automaticamente
2. ✅ Instalar dependências do `requirements_api.txt`
3. ✅ Iniciar os serviços corretamente

## Configuração no Railway

### Build Command
Deixe **VAZIO** - o `nixpacks.toml` cuida disso.

### Start Commands

- **API**: `python api/api_google_sheets.py`
- **Bot**: `python bot/breno_bot.py`
- **Scheduler**: `python bot/scheduler_breno.py`

## Variáveis de Ambiente

Para cada serviço:

```
GOOGLE_CREDENTIALS=<json_completo>
SPREADSHEET_ID=1zK0xBqbcS_05eloUPnTn0k-B3mMYdnk8rjWek5YNSuI
PORT=8000
```

Para Bot e Scheduler, adicione:
```
TELEGRAM_BOT_TOKEN=seu_token
TELEGRAM_CHAT_ID=seu_chat_id
```

## Teste

Após o deploy, verifique os logs. Deve aparecer:
- ✅ Python detectado
- ✅ Dependências instaladas
- ✅ Serviço iniciando
