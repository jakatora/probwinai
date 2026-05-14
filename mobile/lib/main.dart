import 'package:flutter/material.dart';
import 'api/api_client.dart';
import 'screens/home_screen.dart';
import 'screens/paywall_screen.dart';
import 'screens/welcome_screen.dart';
import 'services/subscription_service.dart';
import 'theme.dart';

const String kDataUrl = String.fromEnvironment(
  "API_URL",
  defaultValue: "https://jakatora.github.io/probwinai/data",
);

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final api = ApiClient(baseUrl: kDataUrl);
  final subscription = SubscriptionService();
  await subscription.init();
  final accepted = await hasAccepted();
  runApp(ProbWinAIApp(
    api: api,
    subscription: subscription,
    accepted: accepted,
  ));
}

class ProbWinAIApp extends StatefulWidget {
  final ApiClient api;
  final SubscriptionService subscription;
  final bool accepted;

  const ProbWinAIApp({
    super.key,
    required this.api,
    required this.subscription,
    required this.accepted,
  });

  @override
  State<ProbWinAIApp> createState() => _ProbWinAIAppState();
}

class _ProbWinAIAppState extends State<ProbWinAIApp> {
  late bool _accepted;

  @override
  void initState() {
    super.initState();
    _accepted = widget.accepted;
    widget.subscription.addListener(_onSubChange);
  }

  @override
  void dispose() {
    widget.subscription.removeListener(_onSubChange);
    super.dispose();
  }

  void _onSubChange() {
    if (mounted) setState(() {});
  }

  Widget _home() {
    if (!_accepted) {
      return WelcomeScreen(
        onAccepted: () => setState(() => _accepted = true),
      );
    }
    if (widget.subscription.hasAccess) {
      return HomeScreen(
        api: widget.api,
        subscription: widget.subscription,
      );
    }
    return PaywallScreen(
      subscription: widget.subscription,
      dismissible: false,
      onUnlocked: () => setState(() {}),
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ProbWin AI',
      debugShowCheckedModeBanner: false,
      theme: buildTheme(),
      home: _home(),
    );
  }
}
