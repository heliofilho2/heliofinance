import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'screens/dashboard_screen.dart';
import 'screens/alertas_screen.dart';
import 'screens/relatorio_semanal_screen.dart';
import 'screens/relatorio_mensal_screen.dart';
import 'screens/categorias_screen.dart';
import 'screens/projecao_screen.dart';
import 'utils/colors.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Inicializar locale para pt_BR
  await initializeDateFormatting('pt_BR', null);
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Breno Finance',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: AppColors.primary,
        scaffoldBackgroundColor: AppColors.backgroundLight,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.primary,
          brightness: Brightness.light,
        ),
        textTheme: GoogleFonts.interTextTheme(),
        useMaterial3: true,
      ),
      home: const DashboardScreen(),
      routes: {
        '/alertas': (context) => const AlertasScreen(),
        '/relatorio-semanal': (context) => const RelatorioSemanalScreen(),
        '/relatorio-mensal': (context) => const RelatorioMensalScreen(),
        '/categorias': (context) => const CategoriasScreen(),
        '/projecao': (context) => const ProjecaoScreen(),
      },
    );
  }
}
