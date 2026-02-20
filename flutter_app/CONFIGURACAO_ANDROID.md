# 📱 Configuração Android para APK

## ⚠️ Problema Atual

O Flutter detectou que o Android SDK não está configurado corretamente:
```
X Android toolchain - develop for Android devices
  X ANDROID_HOME = D:\AppData\Local\Android\Sdk
    but Android SDK not found at this location.
```

## ✅ Soluções

### Opção 1: Instalar Android Studio (Recomendado)

1. **Baixar Android Studio:**
   - https://developer.android.com/studio
   - Instale normalmente

2. **Configurar Android SDK:**
   - Abra Android Studio
   - Vá em: `File` → `Settings` → `Appearance & Behavior` → `System Settings` → `Android SDK`
   - Instale:
     - Android SDK Platform-Tools
     - Android SDK Build-Tools
     - Android SDK Platform (API 33 ou superior)
     - Android Emulator

3. **Configurar Variáveis de Ambiente:**
   - Windows: `Win + R` → `sysdm.cpl` → `Avançado` → `Variáveis de Ambiente`
   - Adicione:
     - `ANDROID_HOME` = `C:\Users\SEU_USUARIO\AppData\Local\Android\Sdk`
     - Adicione ao PATH: `%ANDROID_HOME%\platform-tools` e `%ANDROID_HOME%\tools`

4. **Verificar:**
   ```bash
   flutter doctor
   ```

### Opção 2: Usar SDK Standalone (Mais Leve)

1. **Baixar Command Line Tools:**
   - https://developer.android.com/studio#command-tools
   - Extraia para: `D:\Android\Sdk`

2. **Instalar SDK via linha de comando:**
   ```bash
   # Navegue até a pasta tools/bin
   cd D:\Android\Sdk\cmdline-tools\latest\bin
   
   # Aceite licenças
   sdkmanager --licenses
   
   # Instale componentes
   sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"
   ```

3. **Configurar ANDROID_HOME:**
   - `ANDROID_HOME` = `D:\Android\Sdk`
   - PATH: `%ANDROID_HOME%\platform-tools`

### Opção 3: Usar Web/Windows por Enquanto

O app já está configurado para rodar em:
- **Windows Desktop** (já funcionando)
- **Web/Chrome** (já funcionando)

Para testar:
```bash
# Windows
flutter run -d windows

# Web
flutter run -d chrome
```

## 🚀 Gerar APK (Após Configurar Android)

### APK Debug:
```bash
flutter build apk --debug
```
Arquivo: `build/app/outputs/flutter-apk/app-debug.apk`

### APK Release:
```bash
flutter build apk --release
```
Arquivo: `build/app/outputs/flutter-apk/app-release.apk`

### App Bundle (Google Play):
```bash
flutter build appbundle --release
```
Arquivo: `build/app/outputs/bundle/release/app-release.aab`

## 📝 Notas

- **Emulador Android:** Após instalar Android Studio, você pode criar um emulador para testar
- **Dispositivo Físico:** Conecte via USB e habilite "Depuração USB" nas opções de desenvolvedor
- **Verificar dispositivos:** `flutter devices`

## 🔧 Troubleshooting

### Erro: "Android SDK not found"
- Verifique se `ANDROID_HOME` está configurado corretamente
- Reinicie o terminal após configurar variáveis

### Erro: "No devices found"
- Para emulador: Inicie um AVD no Android Studio
- Para dispositivo: Habilite depuração USB e conecte via USB

### Erro: "License not accepted"
```bash
flutter doctor --android-licenses
```

---

**Por enquanto, você pode testar o app em Windows ou Web enquanto configura o Android!**
