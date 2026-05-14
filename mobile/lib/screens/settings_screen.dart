import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../api/api_client.dart';
import '../services/subscription_service.dart';
import '../theme.dart';

class SettingsScreen extends StatelessWidget {
  final ApiClient api;
  final SubscriptionService subscription;
  const SettingsScreen({
    super.key,
    required this.api,
    required this.subscription,
  });

  Future<void> _open(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) await launchUrl(uri, mode: LaunchMode.externalApplication);
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
                  const Text('Subskrypcja',
                      style: TextStyle(
                          color: AppColors.text,
                          fontWeight: FontWeight.w600,
                          fontSize: 16)),
                  const SizedBox(height: 8),
                  Text(
                    subscription.isSubscribed
                        ? 'Aktywna subskrypcja miesieczna. Dziekujemy!'
                        : subscription.trialActive
                            ? 'Darmowy okres: pozostalo '
                                '${subscription.trialDaysLeft} dni.'
                            : 'Darmowy okres zakonczony.',
                    style: const TextStyle(
                        color: AppColors.textDim, fontSize: 13),
                  ),
                  const SizedBox(height: 12),
                  if (subscription.isSubscribed)
                    _LinkRow(
                      label: 'Zarzadzaj subskrypcja',
                      onTap: () => _open(
                          'https://apps.apple.com/account/subscriptions'),
                    )
                  else ...[
                    _LinkRow(
                      label: 'Przywroc zakup',
                      onTap: () => subscription.restore(),
                    ),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text('Dane',
                      style: TextStyle(
                          color: AppColors.text,
                          fontWeight: FontWeight.w600,
                          fontSize: 16)),
                  SizedBox(height: 8),
                  Text(
                    'Top 10 meczow dnia jest odswiezane automatycznie codziennie o 08:00.',
                    style: TextStyle(color: AppColors.textDim, fontSize: 13),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Pomoc i kontakt',
                      style: TextStyle(
                          color: AppColors.text,
                          fontWeight: FontWeight.w600,
                          fontSize: 16)),
                  const SizedBox(height: 12),
                  _LinkRow(
                    label: 'FAQ i wsparcie',
                    onTap: () => _open('https://jakatora.github.io/probwinai/support.html'),
                  ),
                  _LinkRow(
                    label: 'Polityka prywatnosci',
                    onTap: () => _open('https://jakatora.github.io/probwinai/privacy.html'),
                  ),
                  _LinkRow(
                    label: 'Email: kkprotigwelding@gmail.com',
                    onTap: () => _open('mailto:kkprotigwelding@gmail.com'),
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
                    'ProbWin AI v0.1.0',
                    style: TextStyle(color: AppColors.textDim, fontSize: 13),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Aplikacja informacyjna. Nie rekomenduje zakladow. '
                    'Hazard moze uzalezniac. Pomoc: 801 199 990.',
                    style: TextStyle(color: AppColors.warning, fontSize: 12),
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

class _LinkRow extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const _LinkRow({required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10),
        child: Row(
          children: [
            Expanded(
              child: Text(label,
                  style: const TextStyle(color: AppColors.accent2, fontSize: 14)),
            ),
            const Icon(Icons.arrow_forward_ios, color: AppColors.textDim, size: 14),
          ],
        ),
      ),
    );
  }
}
