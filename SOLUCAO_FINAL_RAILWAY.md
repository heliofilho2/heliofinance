# ✅ SOLUÇÃO FINAL: Railway Python Detection

## Problema

O Railway está usando **Railpack** em vez de **Nixpacks**, e não detecta Python corretamente.

## Soluções Aplicadas

### 1. Arquivos Criados

✅ **`requirements.txt`** - Na raiz (Railpack procura isso primeiro)
✅ **`railway.toml`** - Força uso do Nixpacks
✅ **`main.py`** - Ajuda detecção de Python
✅ **`nixpacks.toml`** - Atualizado para usar `python3 -m pip`

### 2. Configuração

O `nixpacks.toml` agora usa:
- `python3 -m pip` (em vez de só `pip`)
- `requirements.txt` (em vez de `requirements_api.txt`)

## ⚠️ IMPORTANTE: Fazer Novo Commit

O Railway está usando um snapshot antigo (mesmo SHA256). Você precisa:

```powershell
# 1. Adicionar todos os novos arquivos
git add .

# 2. Commit
git commit -m "Força detecção Python no Railway - adiciona requirements.txt, railway.toml, main.py"

# 3. Push
git push origin master
```

## Configuração no Railway

### Para cada serviço:

**Builder:** Deixe como está (Metal ou Nixpacks)

**Build Command:** Deixe **VAZIO** - o `nixpacks.toml` cuida

**Start Commands:**

- **API**: `python api/api_google_sheets.py`
- **Bot**: `python bot/breno_bot.py`
- **Scheduler**: `python bot/scheduler_breno.py`

## Se Ainda Não Funcionar

### Opção 1: Forçar Nixpacks no Railway

No Railway, vá em **Settings** → **Build**:
- Mude o **Builder** para **Nixpacks** (se disponível)

### Opção 2: Build Command Manual

Se o Nixpacks não funcionar, use Build Command:

```bash
python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt
```

### Opção 3: Usar Dockerfile

Se nada funcionar, posso criar um `Dockerfile` que força Python.

## Arquivos Importantes

- ✅ `requirements.txt` - Dependências (Railpack procura isso)
- ✅ `runtime.txt` - Versão Python
- ✅ `nixpacks.toml` - Configuração Nixpacks
- ✅ `railway.toml` - Força Nixpacks
- ✅ `main.py` - Ajuda detecção
- ✅ `setup.py` - Ajuda detecção

## Teste

Após o novo deploy, verifique os logs. Deve aparecer:
- ✅ Python sendo detectado
- ✅ `python3 -m pip install` executando
- ✅ Dependências instaladas
- ✅ Serviço iniciando
