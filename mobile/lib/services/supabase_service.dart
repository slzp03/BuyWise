import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/user.dart';
import '../models/purchase.dart';
import '../models/analysis.dart';

/// Supabase CRUD 서비스 (database.py 대응)
class SupabaseService {
  SupabaseService._();
  static final SupabaseService instance = SupabaseService._();

  SupabaseClient get _client => Supabase.instance.client;

  // ============================================
  // Users
  // ============================================

  /// 로그인 시 사용자 조회/생성
  Future<AppUser?> getOrCreateUser({
    required String email,
    String? googleId,
    String? name,
    String? pictureUrl,
  }) async {
    try {
      // 기존 사용자 조회
      final result = await _client
          .from('users')
          .select()
          .eq('email', email)
          .maybeSingle();

      if (result != null) {
        // 기존 사용자 → last_login 업데이트
        await _client.from('users').update({
          'last_login': DateTime.now().toUtc().toIso8601String(),
          'name': name ?? result['name'],
          'picture_url': pictureUrl ?? result['picture_url'],
        }).eq('id', result['id']);
        return AppUser.fromJson(result);
      }

      // 신규 사용자 생성
      final newUser = {
        'email': email,
        'google_id': googleId,
        'name': name ?? '',
        'picture_url': pictureUrl ?? '',
        'usage_count': 0,
        'is_subscribed': false,
        'language': 'ko',
      };
      final inserted =
          await _client.from('users').insert(newUser).select().single();
      return AppUser.fromJson(inserted);
    } catch (e) {
      print('[SupabaseService] getOrCreateUser error: $e');
      return null;
    }
  }

  /// 이메일로 사용자 조회
  Future<AppUser?> getUserByEmail(String email) async {
    try {
      final result = await _client
          .from('users')
          .select()
          .eq('email', email)
          .maybeSingle();
      return result != null ? AppUser.fromJson(result) : null;
    } catch (e) {
      return null;
    }
  }

  /// 사용 횟수 +1
  Future<void> incrementUsage(String userId) async {
    try {
      final result = await _client
          .from('users')
          .select('usage_count, is_subscribed')
          .eq('id', userId)
          .single();

      if (!(result['is_subscribed'] as bool? ?? false)) {
        final current = result['usage_count'] as int? ?? 0;
        await _client
            .from('users')
            .update({'usage_count': current + 1}).eq('id', userId);
      }
    } catch (e) {
      print('[SupabaseService] incrementUsage error: $e');
    }
  }

  /// 언어 설정 저장
  Future<void> updateLanguage(String userId, String lang) async {
    try {
      await _client
          .from('users')
          .update({'language': lang}).eq('id', userId);
    } catch (e) {
      print('[SupabaseService] updateLanguage error: $e');
    }
  }

  // ============================================
  // Purchases
  // ============================================

  /// 개별 구매 1건 저장
  Future<bool> saveSinglePurchase(
      String userId, Purchase purchase) async {
    try {
      final data = purchase.toJson();
      data['user_id'] = userId;
      await _client.from('purchases').insert(data);
      return true;
    } catch (e) {
      print('[SupabaseService] saveSinglePurchase error: $e');
      return false;
    }
  }

  /// 구매 이력 여러 건 저장
  Future<bool> savePurchases(
      String userId, List<Purchase> purchases) async {
    try {
      final rows = purchases.map((p) {
        final data = p.toJson();
        data['user_id'] = userId;
        return data;
      }).toList();

      if (rows.isNotEmpty) {
        await _client.from('purchases').insert(rows);
      }
      return true;
    } catch (e) {
      print('[SupabaseService] savePurchases error: $e');
      return false;
    }
  }

  /// 구매 이력 로드 (기간 필터 지원)
  Future<List<Purchase>> loadPurchases(
    String userId, {
    String? dateFrom,
    String? dateTo,
  }) async {
    try {
      var query = _client
          .from('purchases')
          .select()
          .eq('user_id', userId);

      if (dateFrom != null) {
        query = query.gte('purchase_date', dateFrom);
      }
      if (dateTo != null) {
        query = query.lte('purchase_date', dateTo);
      }

      final result =
          await query.order('purchase_date', ascending: false);

      return (result as List)
          .map((row) => Purchase.fromJson(row as Map<String, dynamic>))
          .toList();
    } catch (e) {
      print('[SupabaseService] loadPurchases error: $e');
      return [];
    }
  }

  /// 선택한 구매 삭제
  Future<bool> deletePurchases(
      String userId, List<int> purchaseIds) async {
    try {
      for (final id in purchaseIds) {
        await _client
            .from('purchases')
            .delete()
            .eq('id', id)
            .eq('user_id', userId);
      }
      return true;
    } catch (e) {
      print('[SupabaseService] deletePurchases error: $e');
      return false;
    }
  }

  /// 구매 이력 수
  Future<int> getPurchaseCount(String userId) async {
    try {
      final result = await _client
          .from('purchases')
          .select('id')
          .eq('user_id', userId)
          .count(CountOption.exact);
      return result.count;
    } catch (e) {
      return 0;
    }
  }

  // ============================================
  // Analyses
  // ============================================

  /// 분석 결과 저장
  Future<int?> saveAnalysis(
      String userId, Analysis analysis) async {
    try {
      final data = analysis.toJson();
      data['user_id'] = userId;
      final result =
          await _client.from('analyses').insert(data).select('id').single();
      return result['id'] as int;
    } catch (e) {
      print('[SupabaseService] saveAnalysis error: $e');
      return null;
    }
  }

  /// 분석 이력 조회 (최신순)
  Future<List<Analysis>> loadAnalyses(
      String userId, {int limit = 10}) async {
    try {
      final result = await _client
          .from('analyses')
          .select()
          .eq('user_id', userId)
          .order('created_at', ascending: false)
          .limit(limit);

      return (result as List)
          .map((row) => Analysis.fromJson(row as Map<String, dynamic>))
          .toList();
    } catch (e) {
      return [];
    }
  }

  // ============================================
  // AI Usage Logs
  // ============================================

  /// AI API 사용량 기록
  Future<void> logAiUsage({
    required String userId,
    int? analysisId,
    required String callType,
    required int promptTokens,
    required int completionTokens,
    required int totalTokens,
  }) async {
    try {
      // gpt-4o-mini 기준 비용
      final promptCost = promptTokens * 0.00000015;
      final completionCost = completionTokens * 0.0000006;
      final estimatedCost = promptCost + completionCost;

      await _client.from('ai_usage_logs').insert({
        'user_id': userId,
        'analysis_id': analysisId,
        'call_type': callType,
        'prompt_tokens': promptTokens,
        'completion_tokens': completionTokens,
        'total_tokens': totalTokens,
        'estimated_cost_usd': double.parse(estimatedCost.toStringAsFixed(6)),
      });
    } catch (e) {
      print('[SupabaseService] logAiUsage error: $e');
    }
  }
}
