# 🔧 Troubleshooting - Erros Comuns

## ❌ "Internal Server Error" ao registrar transação

### Possíveis causas:

1. **API não está rodando**
   - Verifique se a API está rodando: http://localhost:8000/health
   - Inicie a API: `python -m uvicorn app.main:app --reload --port 8000`

2. **Banco de dados não inicializado**
   - O banco é criado automaticamente na primeira execução
   - Verifique se existe `data/finance.db`
   - Se não existir, a API cria ao iniciar

3. **Erro no parser**
   - Teste o parser: `python -c "from bot.parser import CommandParser; p = CommandParser(); print(p.parse('mercado 87'))"`
   - Deve retornar um dicionário com os dados

4. **Erro de conexão**
   - Verifique se a API está acessível
   - Teste: `python test_api.py`

### Solução rápida:

1. **Reinicie a API:**
```bash
python -m uvicorn app.main:app --reload --port 8000
```

2. **Verifique os logs da API** - eles mostrarão o erro exato

3. **Teste manualmente:**
```bash
python test_api.py
```

## ❌ "TELEGRAM_BOT_TOKEN não configurado"

**Solução:**
```powershell
$env:TELEGRAM_BOT_TOKEN="seu_token"
```

Ou use o script:
```bash
.\config_token.ps1
```

## ❌ "ModuleNotFoundError: No module named 'telegram'"

**Solução:**
```bash
pip install python-telegram-bot
```

## ❌ "ModuleNotFoundError: No module named 'bot'"

**Solução:**
O código já foi corrigido. Se ainda ocorrer, execute do diretório raiz:
```bash
cd D:\PESSOAL\PROJETOS - TANGRAM\BRENOPLANILHA
python bot/telegram_bot.py
```

## ❌ Bot não responde

1. Verifique se o token está correto
2. Verifique se a API está rodando
3. Verifique os logs do bot (erros aparecem no terminal)

## ✅ Verificar se tudo está OK

```bash
# 1. Testar banco
python -c "from app.database import init_db; init_db(); print('OK')"

# 2. Testar parser
python -c "from bot.parser import CommandParser; p = CommandParser(); print(p.parse('mercado 87'))"

# 3. Testar API (se estiver rodando)
python test_api.py
```

## 📝 Logs Úteis

A API mostra logs detalhados no terminal. Se houver erro, você verá:
- Traceback completo
- Mensagem de erro
- Linha do código

Use esses logs para identificar o problema exato.
