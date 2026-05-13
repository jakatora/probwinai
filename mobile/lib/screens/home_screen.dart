// ProbWin AI - main list screen
import 'package:flutter/material.dart';
import '../api/api_client.dart';
import '../models/match.dart';
import '../theme.dart';
import '../widgets/match_card.dart';
import 'match_detail_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  final ApiClient api;

  const HomeScreen({super.key, required this.api});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late Future<List<MatchListItem>> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.api.getMatches();
  }

  Future<void> _refresh() async {
    setState(() {
      _future = widget.api.getMatches();
    });
    await _future;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ProbWin AI',
            style: TextStyle(fontWeight: FontWeight.w700)),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(
                  builder: (_) => SettingsScreen(api: widget.api)),
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        color: AppColors.accent2,
        child: FutureBuilder<List<MatchListItem>>(
          future: _future,
          builder: (context, snap) {
            if (snap.connectionState == ConnectionState.waiting) {
              return const Center(
                  child: CircularProgressIndicator(color: AppColors.accent2));
            }
            if (snap.hasError) {
              return _ErrorView(
                  message: snap.error.toString(), onRetry: _refresh);
            }
            final matches = snap.data ?? [];
            if (matches.isEmpty) {
              return _EmptyView(onRetry: _refresh);
            }
            return ListView.builder(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              itemCount: matches.length + 1,
              itemBuilder: (context, i) {
                if (i == 0) return _Header(count: matches.length);
                final m = matches[i - 1];
                return MatchCard(
                  match: m,
                  onTap: () => Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) =>
                          MatchDetailScreen(api: widget.api, matchId: m.id),
                    ),
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  final int count;
  const _Header({required this.count});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Top $count meczow dnia',
              style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 4),
          const Text(
            'Statystyki + analiza AI dla najwazniejszych spotkan',
            style: TextStyle(color: AppColors.textDim, fontSize: 13),
          ),
        ],
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  final String message;
  final Future<void> Function() onRetry;

  const _ErrorView({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.cloud_off, color: AppColors.textDim, size: 64),
            const SizedBox(height: 16),
            const Text('Brak polaczenia z serwerem',
                style: TextStyle(color: AppColors.text, fontSize: 16)),
            const SizedBox(height: 8),
            Text(message,
                textAlign: TextAlign.center,
                style:
                    const TextStyle(color: AppColors.textDim, fontSize: 12)),
            const SizedBox(height: 16),
            ElevatedButton(
                onPressed: () => onRetry(),
                child: const Text('Sprobuj ponownie')),
          ],
        ),
      ),
    );
  }
}

class _EmptyView extends StatelessWidget {
  final Future<void> Function() onRetry;
  const _EmptyView({required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.inbox_outlined,
                color: AppColors.textDim, size: 64),
            const SizedBox(height: 16),
            const Text('Brak meczow do wyswietlenia',
                style: TextStyle(color: AppColors.text, fontSize: 16)),
            const SizedBox(height: 8),
            const Text(
                'Sprawdz polaczenie z internetem i sprobuj ponownie.',
                textAlign: TextAlign.center,
                style: TextStyle(color: AppColors.textDim, fontSize: 12)),
            const SizedBox(height: 16),
            ElevatedButton(
                onPressed: () => onRetry(),
                child: const Text('Odswiez')),
          ],
        ),
      ),
    );
  }
}
