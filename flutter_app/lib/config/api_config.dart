/// Configuração da API
class ApiConfig {
  /// URL base da API
  /// 
  /// Para desenvolvimento local: 'http://localhost:8000'
  /// Para produção (Railway): 'https://seu-app.railway.app'
  /// 
  /// Você pode definir via variável de ambiente:
  /// flutter run --dart-define=API_BASE_URL=https://seu-app.railway.app
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
}
