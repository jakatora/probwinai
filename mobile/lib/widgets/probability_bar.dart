// ProbWin AI - visual probability comparison (model vs bookmaker)
import 'package:flutter/material.dart';
import '../theme.dart';

class ProbabilityBar extends StatelessWidget {
  final String label;
  final double modelProb;
  final double impliedProb;
  final double odds;

  const ProbabilityBar({
    super.key,
    required this.label,
    required this.modelProb,
    required this.impliedProb,
    required this.odds,
  });

  @override
  Widget build(BuildContext context) {
    final edgePct = (modelProb - impliedProb) * 100;
    final edgeColor = AppColors.edgeColor(edgePct);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(label,
                    style: const TextStyle(
                        color: AppColors.text, fontWeight: FontWeight.w600)),
              ),
              Text(odds.toStringAsFixed(2),
                  style: const TextStyle(
                      color: AppColors.textDim, fontWeight: FontWeight.w500)),
              const SizedBox(width: 12),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: edgeColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  '${edgePct >= 0 ? '+' : ''}${edgePct.toStringAsFixed(1)}%',
                  style: TextStyle(
                      color: edgeColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 12),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Stack(
            children: [
              Container(
                height: 24,
                decoration: BoxDecoration(
                  color: AppColors.panel2,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: FractionallySizedBox(
                  widthFactor: modelProb.clamp(0.0, 1.0),
                  child: Container(
                    height: 24,
                    decoration: const BoxDecoration(
                      color: AppColors.accent2,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Model: ${(modelProb * 100).toStringAsFixed(1)}%',
                style: const TextStyle(
                    color: AppColors.text,
                    fontSize: 12,
                    fontWeight: FontWeight.w600),
              ),
              Text(
                'Bukmacher: ${(impliedProb * 100).toStringAsFixed(1)}%',
                style: const TextStyle(color: AppColors.textDim, fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
