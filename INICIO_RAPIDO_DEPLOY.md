# ⚡ Início Rápido - Deploy e APK

## 🎯 Passos Rápidos

### 1️⃣ Configurar URL da API no App

**IMPORTANTE**: Antes de gerar o APK, configure a URL da sua API!

Edite `flutter_app/lib/config/api_config.dart`:

```dart
static const String baseUrl = 'https://SUA-API-RAILWAY.app';  // ← Coloque sua URL aqui
```

Ou use variável de ambiente ao gerar:
```bash
flutter build apk --release --dart-define=API_BASE_URL=https://sua-api.railway.app
```

### 2️⃣ Gerar APK

**Opção A: Usar script PowerShell (mais fácil)**
```powershell
.\GERAR_APK.ps1
```

**Opção B: Manual**
```bash
cd flutter_app
flutter clean
flutter pub get
flutter build apk --release
```

O APK estará em: `flutter_app/build/app/outputs/flutter-apk/app-release.apk`

### 3️⃣ Instalar no Celular

1. Copie `app-release.apk` para o celular
2. No celular: Configurações → Segurança → Permitir fontes desconhecidas
3. Abra o arquivo APK e instale

### 4️⃣ Deploy da API no Railway

1. Acesse https://railway.app
2. Crie novo projeto
3. Conecte seu repositório GitHub
4. Configure variáveis:
   - `GOOGLE_CREDENTIALS_PATH=google-credentials.json`
   - `PORT=8000`
5. Faça upload do `google-credentials.json`
6. Railway vai fazer deploy automaticamente
7. Copie a URL gerada (ex: `https://seu-app.railway.app`)

### 5️⃣ Deploy do Bot no Railway

1. Crie novo serviço no mesmo projeto Railway
2. Configure variáveis:
   - `TELEGRAM_BOT_TOKEN=seu_token`
   - `GOOGLE_CREDENTIALS_PATH=google-credentials.json`
   - `TELEGRAM_CHAT_ID=seu_chat_id`
3. Comando de start: `python bot/breno_bot.py`

### 6️⃣ Deploy do Scheduler (Lembretes)

1. Crie novo serviço no Railway
2. Mesmas variáveis do bot
3. Comando de start: `python bot/scheduler_breno.py`

---

## 🔄 Alternativa: Rodar Localmente

Se não quiser usar Railway, pode rodar tudo na sua máquina:

### Terminal 1: API
```powershell
.\run_api_google_sheets.ps1
```

### Terminal 2: Bot
```powershell
.\run_breno_bot.ps1
```

### Terminal 3: Scheduler
```powershell
.\run_scheduler_breno.ps1
```

**Para o app conectar**: Use o IP da sua máquina na rede local:
- Descubra seu IP: `ipconfig` (Windows) ou `ifconfig` (Linux/Mac)
- Configure no app: `http://192.168.X.X:8000`

---

## ✅ Checklist

- [ ] URL da API configurada no `api_config.dart`
- [ ] APK gerado (`app-release.apk`)
- [ ] APK instalado no celular
- [ ] API rodando (teste: abra URL/api/status no navegador)
- [ ] Bot respondendo (envie `/start` no Telegram)
- [ ] Scheduler rodando (teste aguardando lembrete)

---

## 🆘 Problemas Comuns

**APK não instala**
→ Ative "Fontes desconhecidas" nas configurações do Android

**App não conecta**
→ Verifique se a URL da API está correta
→ Teste a API no navegador primeiro
→ Verifique se tem internet no celular

**Bot não responde**
→ Verifique se está rodando
→ Verifique o token do bot
→ Veja os logs no Railway

---

## 📱 Pronto!

Agora você pode:
- ✅ Usar o app no celular
- ✅ Registrar gastos pelo bot Telegram
- ✅ Receber lembretes automáticos
- ✅ Ver projeções futuras
- ✅ Acompanhar tudo em tempo real!
