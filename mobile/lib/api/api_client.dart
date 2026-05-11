// ProbWin AI - klient danych dla aplikacji.
//
// Wspieramy dwa tryby:
// 1. STATIC (produkcja - GitHub Pages):
//    URL kończacy sie '/data' wskazuje na statyczne JSONy.
//    Lista: GET {baseUrl}/data/top10.json
//    Detal: GET {baseUrl}/data/matches/{id}.json
//
// 2. API (development - FastAPI lokalny / Railway):
//    URL bez '/data' wskazuje na endpointy REST.
//    Lista: GET {baseUrl}/api/matches
//    Detal: GET {baseUrl}/api/matches/{id}
//
// Tryb wykrywany jest automatycznie przez obecnosc '/data' w baseUrl.
// Default produkcja: https://probwinai.github.io/probwinai/data
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/match.dart';

class ApiClient {
  final String baseUrl;
  final http.Client _http;

  ApiClient({
    this.baseUrl = 'https://jakatora.github.io/probwinai/data',
    http.Client? httpClient,
  }) : _http = httpClient ?? http.Client();

  bool get _isStatic => baseUrl.endsWith('/data') || baseUrl.endsWith('/data/');

  /// Lista top N meczow.
  Future<List<MatchListItem>> getMatches({int limit = 50}) async {
    if (_isStatic) {
      // GitHub Pages: pobierz top10.json
      final uri = Uri.parse('${baseUrl.replaceAll(RegExp(r'/$'), '')}/top10.json');
      final r = await _http.get(uri);
      if (r.statusCode != 200) {
        throw ApiException('GET ${uri.path} failed: ${r.statusCode}');
      }
      final data = jsonDecode(r.body) as Map<String, dynamic>;
      final matches = (data['matches'] as List).cast<Map<String, dynamic>>();
      return matches.map(MatchListItem.fromJson).take(limit).toList();
    }

    // REST API (dev mode)
    final uri = Uri.parse('$baseUrl/api/matches?limit=$limit&only_with_insights=true');
    final r = await _http.get(uri);
    if (r.statusCode != 200) {
      throw ApiException('GET /api/matches failed: ${r.statusCode}');
    }
    final List data = jsonDecode(r.body) as List;
    return data
        .map((j) => MatchListItem.fromJson(j as Map<String, dynamic>))
        .toList();
  }

  /// Pelny raport o meczu.
  Future<MatchInsights> getMatchInsights(String matchId) async {
    if (_isStatic) {
      final uri = Uri.parse(
          '${baseUrl.replaceAll(RegExp(r'/$'), '')}/matches/$matchId.json');
      final r = await _http.get(uri);
      if (r.statusCode == 404) {
        throw ApiException('Match not found', statusCode: 404);
      }
      if (r.statusCode != 200) {
        throw ApiException('GET ${uri.path} failed: ${r.statusCode}');
      }
      return MatchInsights.fromJson(jsonDecode(r.body) as Map<String, dynamic>);
    }

    final uri = Uri.parse('$baseUrl/api/matches/$matchId');
    final r = await _http.get(uri);
    if (r.statusCode == 404) {
      throw ApiException('Match not found', statusCode: 404);
    }
    if (r.statusCode != 200) {
      throw ApiException('GET /api/matches/$matchId failed: ${r.statusCode}');
    }
    return MatchInsights.fromJson(jsonDecode(r.body) as Map<String, dynamic>);
  }

  /// Manualny refresh - tylko w trybie API (static jest auto-refresh przez GitHub Actions cron).
  Future<Map<String, dynamic>> refresh({int top = 10}) async {
    if (_isStatic) {
      throw ApiException(
        'Refresh niedostepny w trybie static. '
        'Dane sa odswiezane codziennie przez GitHub Actions.',
      );
    }
    final uri = Uri.parse('$baseUrl/api/refresh?top=$top');
    final r = await _http.post(uri);
    if (r.statusCode != 200) {
      throw ApiException('POST /api/refresh failed: ${r.statusCode}');
    }
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

  bool get supportsManualRefresh => !_isStatic;

  void close() => _http.close();
}

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  ApiException(this.message, {this.statusCode});
  @override
  String toString() => 'ApiException: $message';
}
