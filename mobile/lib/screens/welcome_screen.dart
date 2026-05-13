// ProbWin AI - first-launch welcome with age gate + responsible gambling notice.
// Wymagane dla zatwierdzenia w Google Play / Apple dla aplikacji okolohazardowych.
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import '../theme.dart';

const String _kAcceptedKey = "welcome_accepted_v1";

class WelcomeScreen extends StatefulWidget {
  final VoidCallback onAccepted;
  const WelcomeScreen({super.key, required this.onAccepted});

  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen> {
  bool _ageConfirmed = false;
  bool _termsAccepted = false;

  Future<void> _accept() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_kAcceptedKey, true);
    if (mounted) widget.onAccepted();
  }

  Future<void> _openUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 24),
              const Icon(Icons.analytics, color: AppColors.accent2, size: 64),
              const SizedBox(height: 24),
              const Text(
                "ProbWin AI",
                style: TextStyle(
                    color: AppColors.text,
                    fontSize: 28,
                    fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                "Football statistics & probabilities, powered by AI",
                style: TextStyle(color: AppColors.textDim, fontSize: 14),
              ),
              const SizedBox(height: 32),
              const _NoteCard(
                icon: Icons.info_outline,
                color: AppColors.accent2,
                title: "Czym jest ProbWin AI",
                body: "Aplikacja prezentuje statystyki sportowe i obliczone "
                    "matematycznie prawdopodobienstwa wynikow meczow pilkarskich. "
                    "AI dostarcza komentarz analityczny w prostym jezyku.",
              ),
              const SizedBox(height: 12),
              const _NoteCard(
                icon: Icons.warning_amber,
                color: AppColors.warning,
                title: "Czym NIE jest",
                body: "Aplikacja NIE rekomenduje zakladow, NIE gwarantuje "
                    "zyskow, NIE jest powiazana z zadnym bukmacherem. "
                    "Informacje sluza wylacznie celom edukacyjnym i statystycznym.",
              ),
              const SizedBox(height: 12),
              _NoteCard(
                icon: Icons.health_and_safety,
                color: AppColors.danger,
                title: "Hazard moze uzalezniac",
                body: "Jesli grasz w zaklady bukmacherskie, rob to "
                    "odpowiedzialnie. Bezplatna pomoc w Polsce: ",
                action: GestureDetector(
                  onTap: () => _openUrl("tel:+48801199990"),
                  child: const Text(
                    "tel. 801 199 990",
                    style: TextStyle(
                        color: AppColors.accent2,
                        decoration: TextDecoration.underline,
                        fontWeight: FontWeight.w600),
                  ),
                ),
              ),
              const Spacer(),
              CheckboxListTile(
                value: _ageConfirmed,
                onChanged: (v) => setState(() => _ageConfirmed = v ?? false),
                title: const Text(
                  "Potwierdzam, ze mam ukonczone 18 lat",
                  style: TextStyle(color: AppColors.text, fontSize: 14),
                ),
                activeColor: AppColors.accent,
                checkColor: AppColors.bg,
                contentPadding: EdgeInsets.zero,
                controlAffinity: ListTileControlAffinity.leading,
              ),
              CheckboxListTile(
                value: _termsAccepted,
                onChanged: (v) => setState(() => _termsAccepted = v ?? false),
                title: GestureDetector(
                  onTap: () => _openUrl(
                      "https://jakatora.github.io/probwinai/privacy.html"),
                  child: const Text.rich(
                    TextSpan(
                      style:
                          TextStyle(color: AppColors.text, fontSize: 14),
                      children: [
                        TextSpan(text: "Akceptuje "),
                        TextSpan(
                          text: "regulamin i polityke prywatnosci",
                          style: TextStyle(
                              color: AppColors.accent2,
                              decoration: TextDecoration.underline),
                        ),
                      ],
                    ),
                  ),
                ),
                activeColor: AppColors.accent,
                checkColor: AppColors.bg,
                contentPadding: EdgeInsets.zero,
                controlAffinity: ListTileControlAffinity.leading,
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: (_ageConfirmed && _termsAccepted) ? _accept : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.accent2,
                    foregroundColor: AppColors.bg,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8)),
                  ),
                  child: const Text("Kontynuuj",
                      style: TextStyle(
                          fontSize: 16, fontWeight: FontWeight.w600)),
                ),
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ),
    );
  }
}

Future<bool> hasAccepted() async {
  final prefs = await SharedPreferences.getInstance();
  return prefs.getBool(_kAcceptedKey) ?? false;
}


class _NoteCard extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String body;
  final Widget? action;

  const _NoteCard({
    required this.icon,
    required this.color,
    required this.title,
    required this.body,
    this.action,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: BorderRadius.circular(8),
        border: Border(left: BorderSide(color: color, width: 3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: TextStyle(
                        color: color,
                        fontSize: 13,
                        fontWeight: FontWeight.w700)),
                const SizedBox(height: 4),
                if (action == null)
                  Text(body,
                      style: const TextStyle(
                          color: AppColors.text,
                          fontSize: 13,
                          height: 1.4))
                else
                  Text.rich(
                    TextSpan(
                      style: const TextStyle(
                          color: AppColors.text, fontSize: 13, height: 1.4),
                      children: [
                        TextSpan(text: body),
                        WidgetSpan(
                          child: action!,
                          alignment: PlaceholderAlignment.middle,
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
