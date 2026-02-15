import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../l10n/translations.dart';
import '../config/constants.dart';
import 'login_screen.dart';

/// 설정 화면
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    final user = auth.currentUser;
    final lang = user?.language ?? 'ko';

    return Scaffold(
      appBar: AppBar(
        title: Text(AppTranslations.t('settings', lang: lang)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // 계정 정보 카드
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  // 프로필 사진
                  CircleAvatar(
                    radius: 28,
                    backgroundImage: user?.pictureUrl != null
                        ? NetworkImage(user!.pictureUrl!)
                        : null,
                    child: user?.pictureUrl == null
                        ? const Icon(Icons.person, size: 28)
                        : null,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          user?.name ?? '',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          user?.email ?? '',
                          style: TextStyle(
                              fontSize: 13, color: Colors.grey[600]),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: user?.isSubscribed == true
                                ? Colors.amber[100]
                                : Colors.grey[100],
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            user?.isSubscribed == true
                                ? AppTranslations.t('premium', lang: lang)
                                : '${AppTranslations.t('free_plan', lang: lang)} (${user?.remainingUsage ?? 5}${AppTranslations.t('remaining', lang: lang)})',
                            style: TextStyle(
                              fontSize: 11,
                              color: user?.isSubscribed == true
                                  ? Colors.amber[800]
                                  : Colors.grey[700],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // 언어 설정
          _SettingsSection(
            title: AppTranslations.t('language', lang: lang),
            children: [
              _SettingsTile(
                title: '한국어',
                trailing: lang == 'ko'
                    ? const Icon(Icons.check, color: Color(0xFF6366F1))
                    : null,
                onTap: () => auth.changeLanguage('ko'),
              ),
              _SettingsTile(
                title: '日本語',
                trailing: lang == 'ja'
                    ? const Icon(Icons.check, color: Color(0xFF6366F1))
                    : null,
                onTap: () => auth.changeLanguage('ja'),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // 앱 정보
          _SettingsSection(
            title: AppTranslations.t('about', lang: lang),
            children: [
              _SettingsTile(
                title: AppTranslations.t('version', lang: lang),
                trailing: Text(
                  AppConstants.appVersion,
                  style: TextStyle(color: Colors.grey[500]),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // 로그아웃
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () async {
                await auth.signOut();
                if (context.mounted) {
                  Navigator.of(context).pushAndRemoveUntil(
                    MaterialPageRoute(
                        builder: (_) => const LoginScreen()),
                    (route) => false,
                  );
                }
              },
              icon: const Icon(Icons.logout, color: Colors.red),
              label: Text(
                AppTranslations.t('logout', lang: lang),
                style: const TextStyle(color: Colors.red),
              ),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.red),
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SettingsSection extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _SettingsSection({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 8),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: Colors.grey[600],
            ),
          ),
        ),
        Card(
          child: Column(children: children),
        ),
      ],
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final String title;
  final Widget? trailing;
  final VoidCallback? onTap;

  const _SettingsTile({required this.title, this.trailing, this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(title, style: const TextStyle(fontSize: 14)),
      trailing: trailing,
      onTap: onTap,
      dense: true,
    );
  }
}
