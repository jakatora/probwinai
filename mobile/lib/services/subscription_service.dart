import 'dart:async';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'package:in_app_purchase/in_app_purchase.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Zarzadza dostepem do aplikacji: 3 dni darmowego triala, potem subskrypcja.
///
/// Model:
/// - Pierwsze uruchomienie zapisuje timestamp. Przez 72h pelny dostep.
/// - Po 72h: dostep tylko z aktywna subskrypcja (kupiona przez App Store / Google Play).
/// - Status subskrypcji jest cache'owany lokalnie i odswiezany przez restore/purchase stream.
class SubscriptionService extends ChangeNotifier {
  static const String monthlyProductId = 'com.probwinai.app.monthly';
  static const int trialDurationDays = 3;

  static const String _kFirstLaunch = 'first_launch_ms';
  static const String _kSubscribed = 'is_subscribed';

  final InAppPurchase _iap = InAppPurchase.instance;
  StreamSubscription<List<PurchaseDetails>>? _sub;

  bool _subscribed = false;
  DateTime? _firstLaunch;
  ProductDetails? _monthlyProduct;
  bool _storeAvailable = false;
  bool _purchasePending = false;

  bool get isSubscribed => _subscribed;
  bool get purchasePending => _purchasePending;
  bool get storeAvailable => _storeAvailable;
  ProductDetails? get monthlyProduct => _monthlyProduct;

  /// Cena do wyswietlenia, np. "19,99 zl". Pusta jezeli store niedostepny.
  String get priceLabel => _monthlyProduct?.price ?? '';

  int get trialDaysLeft {
    if (_firstLaunch == null) return trialDurationDays;
    final elapsed = DateTime.now().difference(_firstLaunch!);
    final left = trialDurationDays - elapsed.inDays;
    return left < 0 ? 0 : left;
  }

  bool get trialActive {
    if (_firstLaunch == null) return true;
    return DateTime.now().difference(_firstLaunch!).inHours < trialDurationDays * 24;
  }

  /// Czy uzytkownik moze korzystac z aplikacji (trial trwa LUB ma subskrypcje).
  bool get hasAccess => _subscribed || trialActive;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();

    final stored = prefs.getInt(_kFirstLaunch);
    if (stored == null) {
      _firstLaunch = DateTime.now();
      await prefs.setInt(_kFirstLaunch, _firstLaunch!.millisecondsSinceEpoch);
    } else {
      _firstLaunch = DateTime.fromMillisecondsSinceEpoch(stored);
    }

    _subscribed = prefs.getBool(_kSubscribed) ?? false;

    // in_app_purchase wspiera tylko iOS i Android. Na innych platformach
    // (Windows preview) pomijamy - trial dziala, sklep jest "niedostepny".
    final iapSupported = !kIsWeb && (Platform.isIOS || Platform.isAndroid);
    if (!iapSupported) {
      _storeAvailable = false;
      notifyListeners();
      return;
    }

    _storeAvailable = await _iap.isAvailable();
    if (_storeAvailable) {
      _sub = _iap.purchaseStream.listen(
        _onPurchaseUpdate,
        onDone: () => _sub?.cancel(),
        onError: (_) {},
      );
      await _loadProducts();
      // Odswiez status na starcie - wychwytuje wygasle/odnowione subskrypcje.
      await _iap.restorePurchases();
    }

    notifyListeners();
  }

  Future<void> _loadProducts() async {
    final response = await _iap.queryProductDetails({monthlyProductId});
    if (response.productDetails.isNotEmpty) {
      _monthlyProduct = response.productDetails.first;
    }
  }

  /// Rozpoczyna zakup subskrypcji miesiecznej.
  Future<void> buyMonthly() async {
    if (_monthlyProduct == null) return;
    _purchasePending = true;
    notifyListeners();
    final param = PurchaseParam(productDetails: _monthlyProduct!);
    await _iap.buyNonConsumable(purchaseParam: param);
  }

  /// Przywraca wczesniejszy zakup (wymagane przez Apple).
  Future<void> restore() async {
    _purchasePending = true;
    notifyListeners();
    await _iap.restorePurchases();
    // restorePurchases nie ma callbacku konca - resetujemy flage po krotkim czasie.
    await Future.delayed(const Duration(seconds: 2));
    _purchasePending = false;
    notifyListeners();
  }

  Future<void> _onPurchaseUpdate(List<PurchaseDetails> purchases) async {
    for (final p in purchases) {
      if (p.productID != monthlyProductId) continue;

      switch (p.status) {
        case PurchaseStatus.purchased:
        case PurchaseStatus.restored:
          await _setSubscribed(true);
          break;
        case PurchaseStatus.error:
        case PurchaseStatus.canceled:
          _purchasePending = false;
          break;
        case PurchaseStatus.pending:
          _purchasePending = true;
          break;
      }

      if (p.pendingCompletePurchase) {
        await _iap.completePurchase(p);
      }
    }
    _purchasePending = false;
    notifyListeners();
  }

  Future<void> _setSubscribed(bool value) async {
    _subscribed = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_kSubscribed, value);
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }
}
