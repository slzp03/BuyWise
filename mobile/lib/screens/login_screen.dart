import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../l10n/translations.dart';

/// 로그인 화면
class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    const lang = 'ko'; // 로그인 전 기본 언어

    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // 로고
              const Icon(
                Icons.analytics_outlined,
                size: 100,
                color: Color(0xFF6366F1),
              ),
              const SizedBox(height: 24),

              // 앱 이름
              Text(
                AppTranslations.t('app_title', lang: lang),
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),

              // 설명
              Text(
                AppTranslations.t('app_subtitle', lang: lang),
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 48),

              // 기능 소개 카드
              _FeatureCard(
                icon: Icons.receipt_long,
                title: '가계부',
                description: '일상 소비를 간편하게 기록하세요',
              ),
              const SizedBox(height: 12),
              _FeatureCard(
                icon: Icons.psychology,
                title: 'AI 분석',
                description: '소비 심리를 AI가 분석해드립니다',
              ),
              const SizedBox(height: 12),
              _FeatureCard(
                icon: Icons.trending_down,
                title: '후회 방지',
                description: '충동 구매 패턴을 찾아 개선해요',
              ),
              const SizedBox(height: 48),

              // Google 로그인 버튼
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton.icon(
                  onPressed: auth.isLoading ? null : () => _signIn(context),
                  icon: Image.network(
                    'https://www.google.com/favicon.ico',
                    width: 20,
                    height: 20,
                    errorBuilder: (_, __, ___) =>
                        const Icon(Icons.login, size: 20),
                  ),
                  label: Text(
                    AppTranslations.t('google_login', lang: lang),
                    style: const TextStyle(fontSize: 16),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: Colors.black87,
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: BorderSide(color: Colors.grey[300]!),
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // 무료 플랜 안내
              Text(
                '무료 5회 분석 제공 | 모든 기능 이용 가능',
                style: TextStyle(fontSize: 12, color: Colors.grey[500]),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _signIn(BuildContext context) async {
    final auth = context.read<AuthService>();
    final success = await auth.signInWithGoogle();

    if (!success && context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('로그인에 실패했습니다. 다시 시도해주세요.')),
      );
    }
  }
}

class _FeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;

  const _FeatureCard({
    required this.icon,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFF6366F1), size: 28),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 14)),
                Text(description,
                    style: TextStyle(fontSize: 12, color: Colors.grey[600])),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
