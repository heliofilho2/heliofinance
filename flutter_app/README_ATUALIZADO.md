# 📱 App Flutter - Breno Finance

App Flutter atualizado para consumir a API do Google Sheets.

## ✅ Funcionalidades Implementadas

### Dashboard Principal
- **Status Financeiro**: Saldo atual, performance do mês
- **Semáforo**: Indicador visual (verde/amarelo/vermelho)
- **Resumo do Mês**: Entradas, saídas, gastos diários, performance
- **Gasto Diário**: Progresso em relação ao limite sugerido
- **Alertas**: Seção de alertas ativos no topo

### Novas Telas
- **Alertas** (`/alertas`): Lista todos os alertas financeiros ativos
- **Relatório Semanal** (`/relatorio-semanal`): Top 5 gastos, economia vs previsto, performance
- **Relatório Mensal** (`/relatorio-mensal`): Análise completa, comparativo com mês anterior, insights
- **Categorias** (`/categorias`): Lista todas as categorias de gastos

## 🚀 Como Configurar

### 1. Configurar URL da API

Edite `lib/config/api_config.dart` ou use variável de ambiente:

**Desenvolvimento local:**
```dart
// Já configurado como padrão: 'http://localhost:8000'
```

**Produção (Railway):**
```bash
flutter run --dart-define=API_BASE_URL=https://seu-app.railway.app
```

Ou edite diretamente em `lib/config/api_config.dart`:
```dart
static const String baseUrl = 'https://seu-app.railway.app';
```

### 2. Executar o App

```bash
cd flutter_app
flutter pub get
flutter run
```

## 📋 Endpoints Utilizados

O app consome os seguintes endpoints da API:

- `GET /api/status` - Status financeiro atual
- `GET /api/relatorio/semanal` - Relatório semanal
- `GET /api/relatorio/mensal` - Relatório mensal
- `GET /api/alertas` - Lista de alertas
- `GET /api/categorias` - Lista de categorias

## 🎨 Estrutura de Telas

```
lib/
├── main.dart                    # App principal com rotas
├── config/
│   └── api_config.dart         # Configuração da URL da API
├── screens/
│   ├── dashboard_screen.dart   # Dashboard principal (atualizado)
│   ├── alertas_screen.dart      # Tela de alertas (NOVO)
│   ├── relatorio_semanal_screen.dart  # Relatório semanal (NOVO)
│   ├── relatorio_mensal_screen.dart   # Relatório mensal (NOVO)
│   └── categorias_screen.dart  # Categorias (NOVO)
└── services/
    └── api_service.dart        # Serviço de API (atualizado)
```

## 🔧 Próximos Passos

1. **Testar localmente**: Certifique-se de que a API está rodando em `http://localhost:8000`
2. **Configurar Railway**: Após deploy da API, atualize a URL em `api_config.dart`
3. **Build para produção**: `flutter build apk` ou `flutter build ios`

## 📝 Notas

- O app agora usa dados reais da API ao invés de dados mockados
- Todas as telas têm tratamento de erro e loading states
- Pull-to-refresh está disponível em todas as telas de lista
