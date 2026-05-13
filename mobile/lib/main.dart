import 'package:flutter/material.dart';
import 'api/api_client.dart';
import 'screens/home_screen.dart';
import 'screens/welcome_screen.dart';
import 'theme.dart';

const String kDataUrl = String.fromEnvironment(
  "API_URL",
  defaultValue: "https://jakatora.github.io/probwinai/data",
);

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final api = ApiClient(baseUrl: kDataUrl);
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
