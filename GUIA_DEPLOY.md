# 🚀 Guia de Deploy - Sistema Breno Finance

Este guia explica como gerar o APK do app Flutter e configurar o sistema para rodar em produção.

## 📱 Parte 1: Gerar APK do Flutter

### Pré-requisitos
- Flutter SDK instalado
- Android Studio instalado
- Java JDK instalado
- Variável de ambiente `ANDROID_HOME` configurada

### Passo 1: Configurar URL da API no App

Antes de gerar o APK, você precisa configurar a URL da API que o app vai usar.

**Opção A: API no Railway (Recomendado para produção)**
1. Faça deploy da API no Railway (veja Parte 2)
2. Obtenha a URL do Railway (ex: `https://seu-app.railway.app`)
3. Edite `flutter_app/lib/config/api_config.dart`:
```dart
static const String baseUrl = 'https://seu-app.railway.app';
```

**Opção B: API local (apenas para testes)**
- Use `http://10.0.0.X:8000` (IP da sua máquina na rede local)
- Ou use um serviço como ngrok para expor localhost

### Passo 2: Gerar APK

```bash
cd flutter_app

# 1. Verificar configuração do Flutter
flutter doctor

# 2. Limpar build anterior
flutter clean

# 3. Obter dependências
flutter pub get

# 4. Gerar APK de release
flutter build apk --release

# O APK estará em: flutter_app/build/app/outputs/flutter-apk/app-release.apk
```

### Passo 3: Instalar no Celular

**Método 1: Via USB**
```bash
# Conecte o celular via USB e habilite depuração USB
flutter install
```

**Método 2: Transferir arquivo**
1. Copie `app-release.apk` para o celular
2. No celular, permita instalação de fontes desconhecidas
3. Abra o arquivo e instale

**Método 3: Via Google Drive/Dropbox**
1. Faça upload do APK no Google Drive
2. Acesse pelo celular e baixe
3. Instale o arquivo

---

## 🌐 Parte 2: Deploy da API no Railway

### Passo 1: Criar Conta no Railway
1. Acesse https://railway.app
2. Crie uma conta (pode usar GitHub)

### Passo 2: Criar Novo Projeto
1. Clique em "New Project"
2. Escolha "Deploy from GitHub repo" ou "Empty Project"

### Passo 3: Configurar Variáveis de Ambiente
No Railway, adicione as seguintes variáveis:
```
GOOGLE_CREDENTIALS_PATH=google-credentials.json
PORT=8000
```

### Passo 4: Fazer Upload do Arquivo de Credenciais
1. No Railway, vá em "Variables"
2. Faça upload do arquivo `google-credentials.json`
3. Ou cole o conteúdo JSON na variável `GOOGLE_CREDENTIALS`

### Passo 5: Configurar Deploy
Crie um arquivo `railway.json` na raiz do projeto:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python api/api_google_sheets.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
    }
}
```

Ou crie um `Procfile`:
```
web: python api/api_google_sheets.py
```

### Passo 6: Deploy
1. Conecte seu repositório GitHub ao Railway
2. O Railway vai detectar automaticamente e fazer deploy
3. Aguarde o build completar
4. Anote a URL gerada (ex: `https://seu-app.railway.app`)

---

## 🤖 Parte 3: Deploy do Bot Telegram

### Opção A: Railway (Recomendado)
1. Crie um novo serviço no Railway
2. Configure variáveis:
   - `TELEGRAM_BOT_TOKEN=seu_token`
   - `GOOGLE_CREDENTIALS_PATH=google-credentials.json`
   - `TELEGRAM_CHAT_ID=seu_chat_id`
3. Comando de start: `python bot/breno_bot.py`

### Opção B: Servidor VPS (DigitalOcean, AWS, etc)
1. Conecte via SSH
2. Instale Python 3.10+
3. Clone o repositório
4. Configure ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
pip install -r requirements_api.txt
```
5. Configure variáveis de ambiente
6. Use `screen` ou `tmux` para rodar em background:
```bash
screen -S bot
python bot/breno_bot.py
# Pressione Ctrl+A depois D para sair
```

### Opção C: Servidor Windows (Sua máquina)
Use o script `run_breno_bot.ps1` que já está configurado.

---

## ⏰ Parte 4: Deploy do Scheduler (Lembretes Automáticos)

O scheduler precisa rodar 24/7 para enviar lembretes automáticos.

### Opção A: Railway (mesmo projeto, serviço separado)
1. Crie um novo serviço no Railway
2. Configure as mesmas variáveis do bot
3. Comando de start: `python bot/scheduler_breno.py`

### Opção B: Servidor VPS
```bash
screen -S scheduler
python bot/scheduler_breno.py
```

### Opção C: Windows Task Scheduler
1. Abra "Agendador de Tarefas"
2. Crie nova tarefa
3. Configure para executar `run_scheduler_breno.ps1` na inicialização

---

## 📋 Checklist Final

### Antes de usar no celular:
- [ ] API deployada e funcionando (teste: `curl https://sua-api.railway.app/api/status`)
- [ ] URL da API configurada no `api_config.dart`
- [ ] APK gerado e instalado no celular
- [ ] Bot Telegram rodando e respondendo
- [ ] Scheduler rodando (teste enviando `/status` no bot)

### Testes:
- [ ] App abre sem erros
- [ ] Dashboard carrega dados da API
- [ ] Bot responde comandos
- [ ] Lembretes automáticos funcionam

---

## 🔧 Troubleshooting

### APK não instala no celular
- Verifique se permitiu "Fontes desconhecidas" nas configurações
- Verifique se o APK não está corrompido
- Tente gerar APK novamente: `flutter clean && flutter build apk --release`

### App não conecta à API
- Verifique se a URL está correta no `api_config.dart`
- Teste a API no navegador: `https://sua-api.railway.app/api/status`
- Verifique se o celular tem internet
- Se usando IP local, certifique-se que celular e PC estão na mesma rede

### Bot não responde
- Verifique se o bot está rodando
- Verifique o token do bot
- Verifique logs no Railway/servidor

### Scheduler não envia lembretes
- Verifique se está rodando 24/7
- Verifique logs
- Teste manualmente: `python bot/scheduler_breno.py`

---

## 💡 Dicas

1. **Para desenvolvimento**: Use `flutter run` para testar rapidamente
2. **Para produção**: Use `flutter build apk --release` para APK otimizado
3. **Monitoramento**: Configure alertas no Railway para saber se algo caiu
4. **Backup**: Mantenha backup do arquivo `google-credentials.json` seguro
5. **Segurança**: Nunca commite credenciais no Git

---

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs no Railway
2. Verifique logs do bot/scheduler
3. Teste cada componente isoladamente
4. Verifique variáveis de ambiente
