// ProbWin AI - card showing one match on the home list
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/match.dart';
import '../theme.dart';

class MatchCard extends StatelessWidget {
  final MatchListItem match;
  final VoidCallback? onTap;

  const MatchCard({super.key, required this.match, this.onTap});

  @override
  Widget build(BuildContext context) {
    final dateStr = DateFormat('dd MMM, HH:mm').format(match.kickOff.toLocal());
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(match.league,
                      style: const TextStyle(
                          color: AppColors.textDim, fontSize: 12)),
                  const Spacer(),
                  Text(dateStr,
                      style: const TextStyle(
                          color: AppColors.textDim, fontSize: 12)),
                ],
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: Text(
                      match.homeTeam,
                      style: const TextStyle(
                          color: AppColors.text,
                          fontWeight: FontWeight.w600,
                          fontSize: 16),
                    ),
                  ),
                  const Text('vs',
                      style: TextStyle(
                          color: AppColors.textDim,
                          fontSize: 13,
                          fontWeight: FontWeight.w500)),
                  Expanded(
                    child: Text(
                      match.awayTeam,
                      textAlign: TextAlign.right,
                      style: const TextStyle(
                          color: AppColors.text,
                          fontWeight: FontWeight.w600,
                          fontSize: 16),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  _OddsBox(label: '1', odd: match.odds.home),
                  const SizedBox(width: 8),
                  _OddsBox(label: 'X', odd: match.odds.draw),
                  const SizedBox(width: 8),
                  _OddsBox(label: '2', odd: match.odds.away),
                  const Spacer(),
                  if (match.hasInsights)
                    const Icon(Icons.auto_awesome,
                        color: AppColors.accent2, size: 18),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _OddsBox extends StatelessWidget {
  final String label;
  final double odd;

  const _OddsBox({required this.label, required this.odd});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.panel2,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        children: [
          Text(
            label,
            style: const TextStyle(
                color: AppColors.textDim,
                fontSize: 11,
                fontWeight: FontWeight.w600),
          ),
          const SizedBox(width: 6),
          Text(
            odd.toStringAsFixed(2),
            style: const TextStyle(
                color: AppColors.text,
                fontSize: 13,
                fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}
