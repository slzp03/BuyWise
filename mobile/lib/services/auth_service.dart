import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import 'supabase_service.dart';

/// Google OAuth + 사용자 관리 서비스
class AuthService extends ChangeNotifier {
  AppUser? _currentUser;
  bool _isLoading = false;

  AppUser? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  bool get isLoggedIn => _currentUser != null;

  final GoogleSignIn _googleSignIn = GoogleSignIn(
    scopes: ['email', 'profile'],
  );

  /// 앱 시작 시 자동 로그인 시도
  Future<void> tryAutoLogin() async {
    _isLoading = true;
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      final savedEmail = prefs.getString('user_email');

      if (savedEmail != null) {
        final user = await SupabaseService.instance.getUserByEmail(savedEmail);
        if (user != null) {
          _currentUser = user;
        }
      }
    } catch (e) {
      print('[AuthService] autoLogin error: $e');
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Google 로그인
  Future<bool> signInWithGoogle() async {
    _isLoading = true;
    notifyListeners();

    try {
      final googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        _isLoading = false;
        notifyListeners();
        return false;
      }

      // DB에 사용자 생성/조회
      final user = await SupabaseService.instance.getOrCreateUser(
        email: googleUser.email,
        googleId: googleUser.id,
        name: googleUser.displayName,
        pictureUrl: googleUser.photoUrl,
      );

      if (user != null) {
        _currentUser = user;

        // 이메일 로컬 저장 (자동 로그인용)
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('user_email', googleUser.email);

        _isLoading = false;
        notifyListeners();
        return true;
      }
    } catch (e) {
      print('[AuthService] signIn error: $e');
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  /// 로그아웃
  Future<void> signOut() async {
    try {
      await _googleSignIn.signOut();
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('user_email');
    } catch (e) {
      print('[AuthService] signOut error: $e');
    }

    _currentUser = null;
    notifyListeners();
  }

  /// 사용 가능 여부 체크
  bool get canUse => _currentUser?.canUse ?? true;

  /// 남은 사용 횟수
  int get remainingUsage => _currentUser?.remainingUsage ?? 5;

  /// 사용 횟수 증가
  Future<void> incrementUsage() async {
    if (_currentUser == null) return;

    await SupabaseService.instance.incrementUsage(_currentUser!.id);

    // 로컬 상태 업데이트
    _currentUser = _currentUser!.copyWith(
      usageCount: _currentUser!.usageCount + 1,
    );
    notifyListeners();
  }

  /// 언어 변경
  Future<void> changeLanguage(String lang) async {
    if (_currentUser == null) return;

    await SupabaseService.instance.updateLanguage(_currentUser!.id, lang);

    _currentUser = _currentUser!.copyWith(language: lang);
    notifyListeners();
  }
}
