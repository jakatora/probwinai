// ProbWin AI - detailed match view with AI commentary
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../api/api_client.dart';
import '../models/match.dart';
import '../theme.dart';
import '../widgets/form_indicator.dart';
import '../widgets/probability_bar.dart';

class MatchDetailScreen extends StatefulWidget {
  final ApiClient api;
  final String matchId;

  const MatchDetailScreen({
    super.key,
    required this.api,
    required this.matchId,
  });

  @override
  State<MatchDetailScreen> createState() => _MatchDetailScreenState();
}

class _MatchDetailScreenState extends State<MatchDetailScreen> {
  late Future<MatchInsights> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.api.getMatchInsights(widget.matchId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Analiza meczu')),
      body: FutureBuilder<MatchInsights>(
        future: _future,
        builder: (context, snap) {
          if (snap.connectionState == ConnectionState.waiting) {
            return const Center(
                child: CircularProgressIndicator(color: AppColors.accent2));
          }
          if (snap.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text(snap.error.toString(),
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: AppColors.textDim)),
              ),
            );
          }
          final ins = snap.data!;
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _Header(insights: ins),
                const SizedBox(height: 16),
                if (ins.aiCommentary != null) ...[
                  _CommentaryCard(text: ins.aiCommentary!),
                  const SizedBox(height: 16),
                ],
                _ProbabilityCard(insights: ins),
                const SizedBox(height: 16),
                _TeamsCard(insights: ins),
                const SizedBox(height: 16),
                if (ins.h2h.isNotEmpty) _H2HCard(insights: ins),
                const SizedBox(height: 24),
                _Disclaimer(generatedAt: ins.generatedAt),
                const SizedBox(height: 16),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _Header extends StatelessWidget {
  final MatchInsights insights;
  const _Header({required this.insights});

  @override
  Widget build(BuildContext context) {
    final dateStr =
        DateFormat('dd MMMM yyyy, HH:mm').format(insights.kickOff.toLocal());
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(insights.league,
            style: const TextStyle(color: AppColors.textDim, fontSize: 13)),
        const SizedBox(height: 4),
        Text(
          '${insights.homeTeam} vs ${insights.awayTeam}',
          style: const TextStyle(
              color: AppColors.text,
              fontSize: 24,
              fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(dateStr,
            style: const TextStyle(color: AppColors.textDim, fontSize: 13)),
      ],
    );
  }
}

class _CommentaryCard extends StatelessWidget {
  final String text;
  const _CommentaryCard({required this.text});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.auto_awesome,
                    color: AppColors.accent2, size: 18),
                const SizedBox(width: 8),
                Text('Analiza AI',
                    style: Theme.of(context).textTheme.titleMedium),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.accent2.withOpacity(0.06),
                borderRadius: BorderRadius.circular(8),
                border: const Border(
                  left:
                      BorderSide(color: AppColors.accent2, width: 3),
                ),
              ),
              child: Text(
                text,
                style: const TextStyle(
                    color: AppColors.text, fontSize: 14, height: 1.5),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ProbabilityCard extends StatelessWidget {
  final MatchInsights insights;
  const _ProbabilityCard({required this.insights});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Prawdopodobienstwo wyniku',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            ProbabilityBar(
              label: '1 — ${insights.homeTeam}',
              modelProb: insights.modelProbability.home,
              impliedProb: insights.impliedProbability.home,
              odds: insights.bookmakerOdds.home,
            ),
            ProbabilityBar(
              label: 'X — Remis',
              modelProb: insights.modelProbability.draw,
              impliedProb: insights.impliedProbability.draw,
              odds: insights.bookmakerOdds.draw,
            ),
            ProbabilityBar(
              label: '2 — ${insights.awayTeam}',
              modelProb: insights.modelProbability.away,
              impliedProb: insights.impliedProbability.away,
              odds: insights.bookmakerOdds.away,
            ),
            const SizedBox(height: 8),
            Text(
              'Marza bukmachera (vig): ${insights.vigPct.toStringAsFixed(2)}% • ${insights.bookmakerOdds.bookmaker.replaceAll(RegExp(r"\s*\(mock\)"), "")}',
              style:
                  const TextStyle(color: AppColors.textDim, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
}

class _TeamsCard extends StatelessWidget {
  final MatchInsights insights;
  const _TeamsCard({required this.insights});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Druzyny', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _TeamPanel(ctx: insights.homeContext)),
                const SizedBox(width: 12),
                Expanded(child: _TeamPanel(ctx: insights.awayContext)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _TeamPanel extends StatelessWidget {
  final TeamContext ctx;
  const _TeamPanel({required this.ctx});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.panel2,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(ctx.name,
              style: const TextStyle(
                  color: AppColors.text,
                  fontWeight: FontWeight.w600,
                  fontSize: 15)),
          const SizedBox(height: 8),
          if (ctx.elo != null) ...[
            Text(ctx.elo!.toStringAsFixed(0),
                style: const TextStyle(
                    color: AppColors.accent2,
                    fontSize: 22,
                    fontWeight: FontWeight.bold)),
            const Text('Rating Elo',
                style: TextStyle(color: AppColors.textDim, fontSize: 11)),
          ] else
            const Text('Brak Elo',
                style: TextStyle(color: AppColors.textDim, fontSize: 12)),
          if (ctx.form != null) ...[
            const SizedBox(height: 12),
            FormIndicator(results: ctx.form!.results),
            const SizedBox(height: 6),
            Text(
              '${ctx.form!.points} pkt • ${ctx.form!.goalsFor}-${ctx.form!.goalsAgainst}',
              style: const TextStyle(color: AppColors.textDim, fontSize: 12),
            ),
          ],
        ],
      ),
    );
  }
}

class _H2HCard extends StatelessWidget {
  final MatchInsights insights;
  const _H2HCard({required this.insights});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Ostatnie spotkania (H2H)',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            ...insights.h2h.reversed.map((m) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 80,
                        child: Text(DateFormat('yyyy-MM-dd').format(m.date),
                            style: const TextStyle(
                                color: AppColors.textDim, fontSize: 12)),
                      ),
                      Expanded(
                        child: Text(m.homeTeam,
                            textAlign: TextAlign.right,
                            style: const TextStyle(
                                color: AppColors.text, fontSize: 13)),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.panel2,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(m.score,
                            style: const TextStyle(
                                color: AppColors.text,
                                fontWeight: FontWeight.bold,
                                fontSize: 13)),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(m.awayTeam,
                            style: const TextStyle(
                                color: AppColors.text, fontSize: 13)),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }
}

class _Disclaimer extends StatelessWidget {
  final DateTime generatedAt;
  const _Disclaimer({required this.generatedAt});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          'Wygenerowano: ${DateFormat('yyyy-MM-dd HH:mm').format(generatedAt.toLocal())}',
          style: const TextStyle(color: AppColors.textDim, fontSize: 11),
        ),
        const SizedBox(height: 8),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 24),
          child: Text(
            'ProbWin AI to narzedzie informacyjne. Nie rekomenduje zakladow. '
            'Hazard moze uzalezniać. Graj odpowiedzialnie.',
            textAlign: TextAlign.center,
            style: TextStyle(
                color: AppColors.warning, fontSize: 11, height: 1.4),
          ),
        ),
      ],
    );
  }
}
