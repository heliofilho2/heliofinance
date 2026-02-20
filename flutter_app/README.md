# 📱 Breno Finance - App Flutter

Sistema de gestão financeira pessoal baseado no método Breno, com dashboard moderno e funcionalidades de previsão/projeção.

## 🎯 Funcionalidades

- ✅ **Dashboard Moderno** - Inspirado no design fornecido
- ✅ **Projeção Financeira** - Visualização de saldo e performance futura
- ✅ **Simulação de Empréstimos** - Calcule impacto antes de contratar
- ✅ **Simulação de Compras** - Veja impacto de compras parceladas
- ✅ **Semáforo Financeiro** - Indicador visual de saúde financeira
- ✅ **Transações Recentes** - Histórico rápido de movimentações
- ✅ **Gráficos Interativos** - Visualização de projeções futuras

## 📋 Pré-requisitos

- Flutter SDK 3.0.0 ou superior
- Dart 3.0.0 ou superior
- API Backend rodando em `http://localhost:8000` (ou configurar URL)

## 🚀 Instalação

1. **Instalar dependências:**
```bash
cd flutter_app
flutter pub get
```

2. **Configurar URL da API (opcional):**
Edite `lib/services/api_service.dart` e altere o `baseUrl` se necessário:
```dart
ApiService({
  this.baseUrl = 'http://SEU_IP:8000', // Para dispositivo físico
  // ou
  this.baseUrl = 'http://10.0.2.2:8000', // Para emulador Android
})
```

3. **Executar o app:**
```bash
flutter run
```

## 📱 Estrutura do Projeto

```
lib/
├── main.dart                 # Ponto de entrada
├── models/                   # Modelos de dados
│   ├── dashboard_model.dart
│   └── transaction_model.dart
├── services/                 # Serviços de API
│   └── api_service.dart
├── screens/                  # Telas
│   ├── dashboard_screen.dart
│   ├── simulation_screen.dart
│   ├── projection_screen.dart
│   └── projection_impact_screen.dart
├── widgets/                  # Widgets reutilizáveis
│   ├── balance_card.dart
│   ├── traffic_light_indicator.dart
│   ├── budget_progress_card.dart
│   ├── transaction_item.dart
│   └── projection_chart.dart
└── utils/                    # Utilitários
    ├── colors.dart
    └── formatters.dart
```

## 🎨 Design

O app segue o design fornecido no HTML, com:
- Cores primárias: `#1a227f`
- Semáforo financeiro: Verde/Amarelo/Vermelho
- Cards modernos com sombras e bordas arredondadas
- Tipografia Inter
- Layout responsivo

## 🔌 Integração com API

O app consome a API REST do backend Python:
- `GET /api/dashboard` - Dashboard completo
- `POST /api/transactions/quick` - Criar transação rápida
- `POST /api/simulate/loan` - Simular empréstimo
- `POST /api/simulate/installment` - Simular compra parcelada

## 📊 Funcionalidades de Previsão

### Projeção de Saldo
- Visualiza saldo projetado para próximos 6-12 meses
- Considera receitas médias, fixos, variáveis e parcelas
- Gráfico interativo com FL Chart

### Simulação de Impacto
- Simule empréstimos e veja impacto mensal
- Simule compras parceladas
- Visualize mudanças no saldo e performance
- Semáforo indica viabilidade

## 🛠️ Desenvolvimento

### Executar em modo debug:
```bash
flutter run
```

### Build APK:
```bash
flutter build apk --release
```

### Build para Android:
```bash
flutter build appbundle --release
```

## 📝 Notas

- O app requer que a API backend esteja rodando
- Para testar em dispositivo físico, use o IP da máquina no `baseUrl`
- Para emulador Android, use `10.0.2.2:8000`

## 🔄 Próximos Passos

- [ ] Adicionar autenticação
- [ ] Cache local de dados
- [ ] Notificações push
- [ ] Exportação de relatórios
- [ ] Modo escuro completo

---

**Desenvolvido para uso pessoal com foco em simplicidade e clareza financeira.**
