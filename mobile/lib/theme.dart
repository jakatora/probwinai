// ProbWin AI - app-wide theme & colors
import 'package:flutter/material.dart';

class AppColors {
  static const bg = Color(0xFF0F1419);
  static const panel = Color(0xFF1A212A);
  static const panel2 = Color(0xFF232C38);
  static const text = Color(0xFFE6EDF3);
  static const textDim = Color(0xFF8B9BAB);
  static const accent = Color(0xFF4ADE80);
  static const accent2 = Color(0xFF60A5FA);
  static const warning = Color(0xFFFBBF24);
  static const danger = Color(0xFFF87171);
  static const border = Color(0xFF2D3748);

  static Color edgeColor(double edgePct) {
    if (edgePct > 3) return accent;
    if (edgePct < -3) return danger;
    return textDim;
  }

  static Color formColor(String r) {
    switch (r) {
      case 'W':
        return accent;
      case 'D':
        return warning;
      case 'L':
        return danger;
    }
    return textDim;
  }
}

ThemeData buildTheme() => ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AppColors.bg,
      colorScheme: const ColorScheme.dark(
        surface: AppColors.panel,
        primary: AppColors.accent2,
        secondary: AppColors.accent,
        error: AppColors.danger,
      ),
      cardTheme: const CardThemeData(
        color: AppColors.panel,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(10)),
          side: BorderSide(color: AppColors.border, width: 1),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.bg,
        foregroundColor: AppColors.text,
        elevation: 0,
        centerTitle: false,
      ),
      textTheme: const TextTheme(
        headlineSmall: TextStyle(color: AppColors.text, fontWeight: FontWeight.bold),
        titleMedium: TextStyle(color: AppColors.text, fontWeight: FontWeight.w600),
        bodyMedium: TextStyle(color: AppColors.text),
        bodySmall: TextStyle(color: AppColors.textDim),
      ),
    );
