// ProbWin AI - simple settings screen (API URL, manual refresh)
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../api/api_client.dart';
import '../theme.dart';

class SettingsScreen extends StatefulWidget {
  final ApiClient api;
  const SettingsScreen({super.key, required this.api});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _urlController = TextEditingController();
  bool _refreshing = false;
  String? _refreshResult;

  @override
  void initState() {
    super.initState();
    _loadUrl();
  }

  Future<void> _loadUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString('api_url');
    _urlController.text = saved ?? widget.api.baseUrl;
  }

  Future<void> _saveUrl() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('api_url', _urlController.text);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Zapisano. Uruchom aplikacje ponownie.')),
      );
    }
  }

  Future<void> _runRefresh() async {
    setState(() {
      _refreshing = true;
      _refreshResult = null;
    });
    try {
      final result = await widget.api.refresh();
      setState(() {
        _refreshResult =
            'Pobrano ${result['matches_fetched']} meczow, '
            'wygenerowano insights dla ${result['insights_generated']}.';
      });
    } catch (e) {
      setState(() => _refreshResult = 'Blad: $e');
    } finally {
      if (mounted) setState(() => _refreshing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Ustawienia')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Adres serwera API',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 4),
                  const Text(
                    'Lokalny dev (emulator Android): http://10.0.2.2:8000\n'
                    'Lokalny dev (iOS sim): http://localhost:8000',
                    style:
                        TextStyle(color: AppColors.textDim, fontSize: 12),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _urlController,
                    decoration: const InputDecoration(
                      hintText: 'http://...',
                      border: OutlineInputBorder(),
                    ),
                    style: const TextStyle(color: AppColors.text),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton(
                      onPressed: _saveUrl, child: const Text('Zapisz')),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          if (widget.api.supportsManualRefresh) Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Refresh danych',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 4),
                  const Text(
                    'Reczne odswiezenie top 10 meczow (zwykle robi cron na serwerze).',
                    style: TextStyle(color: AppColors.textDim, fontSize: 12),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: _refreshing ? null : _runRefresh,
                    child: _refreshing
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Odswiez teraz'),
                  ),
                  if (_refreshResult != null) ...[
                    const SizedBox(height: 12),
                    Text(_refreshResult!,
                        style: const TextStyle(
                            color: AppColors.textDim, fontSize: 13)),
                  ],
                ],
              ),
            ),
          )
          else Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Refresh danych',
                      style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 4),
                  const Text(
                    'Dane sa odswiezane automatycznie codziennie o 08:00.',
                    style: TextStyle(color: AppColors.textDim, fontSize: 12),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('O aplikacji',
                      style: TextStyle(
                          color: AppColors.text,
                          fontWeight: FontWeight.w600,
                          fontSize: 16)),
                  SizedBox(height: 8),
                  Text(
                    'ProbWin AI v0.1.0 — sport analytics z AI.',
                    style:
                        TextStyle(color: AppColors.textDim, fontSize: 13),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Aplikacja informacyjna. Nie rekomenduje zakladow. '
                    'Hazard moze uzalezniać. Pomoc: 801 199 990.',
                    style:
                        TextStyle(color: AppColors.warning, fontSize: 12),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
