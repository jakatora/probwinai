// ProbWin AI - data models (mirror of backend pydantic schemas)

class MatchOdds {
  final double home;
  final double draw;
  final double away;
  final String bookmaker;

  MatchOdds({
    required this.home,
    required this.draw,
    required this.away,
    required this.bookmaker,
  });

  factory MatchOdds.fromJson(Map<String, dynamic> json) => MatchOdds(
        home: (json['home'] as num).toDouble(),
        draw: (json['draw'] as num).toDouble(),
        away: (json['away'] as num).toDouble(),
        bookmaker: json['bookmaker'] as String? ?? 'Unknown',
      );
}

class Probability {
  final double home;
  final double draw;
  final double away;

  Probability({required this.home, required this.draw, required this.away});

  factory Probability.fromJson(Map<String, dynamic> json) => Probability(
        home: (json['home'] as num).toDouble(),
        draw: (json['draw'] as num).toDouble(),
        away: (json['away'] as num).toDouble(),
      );
}

class FormSummary {
  final int lastN;
  final List<String> results; // 'W' | 'D' | 'L'
  final int points;
  final int goalsFor;
  final int goalsAgainst;

  FormSummary({
    required this.lastN,
    required this.results,
    required this.points,
    required this.goalsFor,
    required this.goalsAgainst,
  });

  factory FormSummary.fromJson(Map<String, dynamic> json) => FormSummary(
        lastN: json['last_n'] as int,
        results: (json['results'] as List).cast<String>(),
        points: json['points'] as int,
        goalsFor: json['goals_for'] as int,
        goalsAgainst: json['goals_against'] as int,
      );
}

class H2HMatch {
  final DateTime date;
  final String homeTeam;
  final String awayTeam;
  final int homeGoals;
  final int awayGoals;

  H2HMatch({
    required this.date,
    required this.homeTeam,
    required this.awayTeam,
    required this.homeGoals,
    required this.awayGoals,
  });

  String get score => '$homeGoals-$awayGoals';

  factory H2HMatch.fromJson(Map<String, dynamic> json) => H2HMatch(
        date: DateTime.parse(json['date'] as String),
        homeTeam: json['home_team'] as String,
        awayTeam: json['away_team'] as String,
        homeGoals: json['home_goals'] as int,
        awayGoals: json['away_goals'] as int,
      );
}

class TeamContext {
  final String name;
  final double? elo;
  final FormSummary? form;

  TeamContext({required this.name, this.elo, this.form});

  factory TeamContext.fromJson(Map<String, dynamic> json) => TeamContext(
        name: json['name'] as String,
        elo: (json['elo'] as num?)?.toDouble(),
        form: json['form'] != null
            ? FormSummary.fromJson(json['form'] as Map<String, dynamic>)
            : null,
      );
}

class MatchListItem {
  final String id;
  final String homeTeam;
  final String awayTeam;
  final String league;
  final DateTime kickOff;
  final MatchOdds odds;
  final bool hasInsights;

  MatchListItem({
    required this.id,
    required this.homeTeam,
    required this.awayTeam,
    required this.league,
    required this.kickOff,
    required this.odds,
    required this.hasInsights,
  });

  factory MatchListItem.fromJson(Map<String, dynamic> json) => MatchListItem(
        id: json['id'] as String,
        homeTeam: json['home_team'] as String,
        awayTeam: json['away_team'] as String,
        league: json['league'] as String,
        kickOff: DateTime.parse(json['kick_off'] as String),
        odds: MatchOdds.fromJson(json['odds'] as Map<String, dynamic>),
        hasInsights: json['has_insights'] as bool? ?? false,
      );
}

class MatchInsights {
  final String homeTeam;
  final String awayTeam;
  final String league;
  final DateTime kickOff;
  final TeamContext homeContext;
  final TeamContext awayContext;
  final List<H2HMatch> h2h;
  final Probability modelProbability;
  final Probability impliedProbability;
  final MatchOdds bookmakerOdds;
  final double vigPct;
  final String? aiCommentary;
  final DateTime generatedAt;

  MatchInsights({
    required this.homeTeam,
    required this.awayTeam,
    required this.league,
    required this.kickOff,
    required this.homeContext,
    required this.awayContext,
    required this.h2h,
    required this.modelProbability,
    required this.impliedProbability,
    required this.bookmakerOdds,
    required this.vigPct,
    this.aiCommentary,
    required this.generatedAt,
  });

  Map<String, double> edges() => {
        'home': modelProbability.home - impliedProbability.home,
        'draw': modelProbability.draw - impliedProbability.draw,
        'away': modelProbability.away - impliedProbability.away,
      };

  factory MatchInsights.fromJson(Map<String, dynamic> json) => MatchInsights(
        homeTeam: json['home_team'] as String,
        awayTeam: json['away_team'] as String,
        league: json['league'] as String,
        kickOff: DateTime.parse(json['kick_off'] as String),
        homeContext:
            TeamContext.fromJson(json['home_context'] as Map<String, dynamic>),
        awayContext:
            TeamContext.fromJson(json['away_context'] as Map<String, dynamic>),
        h2h: (json['h2h'] as List)
            .map((e) => H2HMatch.fromJson(e as Map<String, dynamic>))
            .toList(),
        modelProbability: Probability.fromJson(
            json['model_probability'] as Map<String, dynamic>),
        impliedProbability: Probability.fromJson(
            json['implied_probability'] as Map<String, dynamic>),
        bookmakerOdds:
            MatchOdds.fromJson(json['bookmaker_odds'] as Map<String, dynamic>),
        vigPct: (json['vig_pct'] as num).toDouble(),
        aiCommentary: json['ai_commentary'] as String?,
        generatedAt: DateTime.parse(json['generated_at'] as String),
      );
}
