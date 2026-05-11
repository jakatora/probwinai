// ProbWin AI - mobile app entry point
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api/api_client.dart';
import 'screens/home_screen.dart';
import 'screens/welcome_screen.dart';
import 'theme.dart';

// Domyslny URL danych wstrzykiwany w czasie kompilacji.
//
// Produkcja (GitHub Pages):
//   flutter build apk --release --dart-define=API_URL=https://[user].github.io/probwinai/data
//
// Development (lokalny FastAPI):
//   flutter run --dart-define=API_URL=http://10.0.2.2:8000
//
// Bez --dart-define uzyje GitHub Pages defaultu.
const String kBuildtimeApiUrl = String.fromEnvironment(
  "API_URL",
  defaultValue: "https://jakatora.github.io/probwinai/data",
);

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  // Hierarchia: zapisana wartosc uzytkownika > buildtime define > GitHub Pages default
  final apiUrl = prefs.getString('api_url') ?? kBuildtimeApiUrl;
  final api = ApiClient(baseUrl: apiUrl);
  final accepted = await hasAccepted();
  runApp(ProbWinAIApp(api: api, accepted: accepted));
}

class ProbWinAIApp extends StatefulWidget {
  final ApiClient api;
  final bool accepted;
  const ProbWinAIApp({super.key, required this.api, required this.accepted});

  @override
  State<ProbWinAIApp> createState() => _ProbWinAIAppState();
}

class _ProbWinAIAppState extends State<ProbWinAIApp> {
  late bool _accepted;

  @override
  void initState() {
    super.initState();
    _accepted = widget.accepted;
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ProbWin AI',
      debugShowCheckedModeBanner: false,
      theme: buildTheme(),
      home: _accepted
          ? HomeScreen(api: widget.api)
          : WelcomeScreen(onAccepted: () => setState(() => _accepted = true)),
    );
  }
}
