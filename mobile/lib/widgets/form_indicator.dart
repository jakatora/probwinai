// ProbWin AI - last-5-matches form indicator (colored dots)
import 'package:flutter/material.dart';
import '../theme.dart';

class FormIndicator extends StatelessWidget {
  final List<String> results; // W / D / L

  const FormIndicator({super.key, required this.results});

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 4,
      children: results.map((r) {
        final color = AppColors.formColor(r);
        return Container(
          width: 24,
          height: 24,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            r,
            style: TextStyle(
                color: color, fontSize: 11, fontWeight: FontWeight.bold),
          ),
        );
      }).toList(),
    );
  }
}
