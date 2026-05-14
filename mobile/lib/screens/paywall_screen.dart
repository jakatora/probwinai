import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/subscription_service.dart';
import '../theme.dart';

/// Ekran blokujacy dostep po wygasnieciu 3-dniowego triala.
/// Pokazuje sie tez gdy trial trwa, jako "soft" zacheta (z mozliwoscia zamkniecia).
class PaywallScreen extends StatefulWidget {
  final SubscriptionService subscription;

  /// Gdy true - uzytkownik moze zamknac paywall (trial wciaz aktywny).
  /// Gdy false - paywall blokuje, jedyne wyjscie to zakup lub restore.
  final bool dismissible;

  /// Wywolane gdy uzytkownik uzyska dostep (kupil / przywrocil).
  final VoidCallback onUnlocked;

  const PaywallScreen({
    super.key,
    required this.subscription,
    required this.onUnlocked,
    this.dismissible = false,
  });

  @override
  State<PaywallScreen> createState() => _PaywallScreenState();
}

class _PaywallScreenState extends State<PaywallScreen> {
  @override
  void initState() {
    super.initState();
    widget.subscription.addListener(_onChange);
  }

  @override
  void dispose() {
    widget.subscription.removeListener(_onChange);
    super.dispose();
  }

  void _onChange() {
    if (!mounted) return;
    if (widget.subscription.isSubscribed) {
      widget.onUnlocked();
    } else {
      setState(() {});
    }
  }

  Future<void> _open(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final sub = widget.subscription;
    final price = sub.priceLabel.isNotEmpty ? sub.priceLabel : '19,99 zl';

    return Scaffold(
      backgroundColor: AppColors.bg,
      body: SafeArea(
        child: Stack(
          children: [
            SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(24, 32, 24, 32),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 24),
                  const Icon(Icons.workspace_premium,
                      color: AppColors.accent2, size: 64),
                  const SizedBox(height: 20),
                  Text(
                    sub.trialActive
                        ? 'Twoj darmowy okres'
                        : 'Darmowy okres zakonczony',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                        color: AppColors.text,
                        fontSize: 26,
                        fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    sub.trialActive
                        ? 'Masz jeszcze ${sub.trialDaysLeft} '
                            '${_dni(sub.trialDaysLeft)} darmowego dostepu. '
                            'Subskrybuj, aby korzystac bez przerwy.'
                        : 'Aby dalej korzystac z ProbWin AI, '
                            'wykup subskrypcje miesieczna.',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                        color: AppColors.textDim, fontSize: 15),
                  ),
                  const SizedBox(height: 32),

                  _benefitRow('Top 10 meczow dnia z analiza'),
                  _benefitRow('Prawdopodobienstwa wynikow'),
                  _benefitRow('Komentarz AI dla kazdego meczu'),
                  _benefitRow('Codzienne odswiezanie danych'),

                  const SizedBox(height: 32),

                  // Karta planu
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: AppColors.panel,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.accent2, width: 2),
                    ),
                    child: Column(
                      children: [
                        const Text('Plan miesieczny',
                            style: TextStyle(
                                color: AppColors.text,
                                fontSize: 18,
                                fontWeight: FontWeight.w700)),
                        const SizedBox(height: 4),
                        Text('$price / miesiac',
                            style: const TextStyle(
                                color: AppColors.accent2,
                                fontSize: 24,
                                fontWeight: FontWeight.w800)),
                        const SizedBox(height: 4),
                        const Text('Odnawia sie automatycznie. Anuluj w kazdej chwili.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                                color: AppColors.textDim, fontSize: 12)),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Przycisk subskrypcji
                  ElevatedButton(
                    onPressed: (sub.purchasePending || !sub.storeAvailable)
                        ? null
                        : () => sub.buyMonthly(),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.accent2,
                      foregroundColor: AppColors.bg,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                    ),
                    child: sub.purchasePending
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: AppColors.bg),
                          )
                        : Text('Subskrybuj za $price / mies.',
                            style: const TextStyle(
                                fontSize: 16, fontWeight: FontWeight.w700)),
                  ),

                  const SizedBox(height: 12),

                  // Restore purchases (wymagane przez Apple)
                  TextButton(
                    onPressed:
                        sub.purchasePending ? null : () => sub.restore(),
                    child: const Text('Przywroc zakup',
                        style: TextStyle(color: AppColors.textDim)),
                  ),

                  if (!sub.storeAvailable)
                    const Padding(
                      padding: EdgeInsets.only(top: 8),
                      child: Text(
                        'Sklep niedostepny na tym urzadzeniu.',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                            color: AppColors.warning, fontSize: 12),
                      ),
                    ),

                  const SizedBox(height: 24),

                  // Linki prawne - wymagane przez Apple przy subskrypcjach
                  Wrap(
                    alignment: WrapAlignment.center,
                    spacing: 16,
                    children: [
                      GestureDetector(
                        onTap: () => _open(
                            'https://jakatora.github.io/probwinai/privacy.html'),
                        child: const Text('Polityka prywatnosci',
                            style: TextStyle(
                                color: AppColors.accent2, fontSize: 12)),
                      ),
                      GestureDetector(
                        onTap: () => _open(
                            'https://jakatora.github.io/probwinai/terms.html'),
                        child: const Text('Warunki korzystania',
                            style: TextStyle(
                                color: AppColors.accent2, fontSize: 12)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Platnosc zostanie pobrana z konta App Store. '
                    'Subskrypcja odnawia sie automatycznie chyba ze zostanie '
                    'anulowana min. 24h przed koncem okresu. Zarzadzaj '
                    'subskrypcja w ustawieniach konta App Store.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: AppColors.textDim, fontSize: 11),
                  ),
                ],
              ),
            ),

            // Przycisk zamkniecia gdy trial wciaz aktywny
            if (widget.dismissible)
              Positioned(
                top: 8,
                right: 8,
                child: IconButton(
                  icon: const Icon(Icons.close, color: AppColors.textDim),
                  onPressed: () => Navigator.of(context).maybePop(),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _benefitRow(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          const Icon(Icons.check_circle, color: AppColors.accent, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(text,
                style: const TextStyle(
                    color: AppColors.text, fontSize: 15)),
          ),
        ],
      ),
    );
  }

  String _dni(int n) {
    if (n == 1) return 'dzien';
    return 'dni';
  }
}
