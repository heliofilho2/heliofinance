# 🔧 Correção: Railway não detecta Python

## Problema

O Railway está dando erro `pip: not found` porque não está detectando Python corretamente.

## Soluções Aplicadas

### 1. Criado `nixpacks.toml`

Este arquivo força o Railway a usar Python 3.12 e instalar as dependências.

### 2. Criado `build.sh`

Script de build alternativo caso o Railway não use o nixpacks.toml.

## ⚠️ IMPORTANTE: Remover `venv/` do Git

O `venv/` está sendo enviado para o Railway, o que pode confundir o detector. Execute:

```powershell
# Remover venv do Git (mas manter localmente)
git rm -r --cached venv/

# Commit
git add .gitignore
git commit -m "Remove venv do Git"

# Push
git push origin master
```

## Configuração no Railway

### Para cada serviço, configure:

**Build Command:**
```
pip install -r requirements_api.txt
```

Ou deixe vazio - o `nixpacks.toml` deve cuidar disso.

**Start Commands:**

- **API**: `python api/api_google_sheets.py`
- **Bot**: `python bot/breno_bot.py`  
- **Scheduler**: `python bot/scheduler_breno.py`

## Se ainda não funcionar

1. No Railway, vá em **Settings** → **Build Command**
2. Remova qualquer comando e deixe vazio
3. O `nixpacks.toml` deve ser usado automaticamente

Ou configure manualmente:

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements_api.txt
```

## Verificar se funcionou

Após o deploy, verifique os logs. Você deve ver:
- ✅ Python sendo detectado
- ✅ Dependências sendo instaladas
- ✅ Serviço iniciando
