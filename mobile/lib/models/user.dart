/// 사용자 모델
class AppUser {
  final String id;
  final String email;
  final String? googleId;
  final String name;
  final String? pictureUrl;
  final int usageCount;
  final bool isSubscribed;
  final String language;
  final DateTime? lastLogin;
  final DateTime? createdAt;

  const AppUser({
    required this.id,
    required this.email,
    this.googleId,
    required this.name,
    this.pictureUrl,
    this.usageCount = 0,
    this.isSubscribed = false,
    this.language = 'ko',
    this.lastLogin,
    this.createdAt,
  });

  factory AppUser.fromJson(Map<String, dynamic> json) {
    return AppUser(
      id: json['id'] as String,
      email: json['email'] as String,
      googleId: json['google_id'] as String?,
      name: json['name'] as String? ?? '',
      pictureUrl: json['picture_url'] as String?,
      usageCount: json['usage_count'] as int? ?? 0,
      isSubscribed: json['is_subscribed'] as bool? ?? false,
      language: json['language'] as String? ?? 'ko',
      lastLogin: json['last_login'] != null
          ? DateTime.parse(json['last_login'] as String)
          : null,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'google_id': googleId,
      'name': name,
      'picture_url': pictureUrl,
      'usage_count': usageCount,
      'is_subscribed': isSubscribed,
      'language': language,
    };
  }

  AppUser copyWith({
    String? name,
    String? pictureUrl,
    int? usageCount,
    bool? isSubscribed,
    String? language,
  }) {
    return AppUser(
      id: id,
      email: email,
      googleId: googleId,
      name: name ?? this.name,
      pictureUrl: pictureUrl ?? this.pictureUrl,
      usageCount: usageCount ?? this.usageCount,
      isSubscribed: isSubscribed ?? this.isSubscribed,
      language: language ?? this.language,
      lastLogin: lastLogin,
      createdAt: createdAt,
    );
  }

  /// 무료 사용 가능 여부
  bool get canUse => isSubscribed || usageCount < 5;

  /// 남은 사용 횟수 (-1 = 무제한)
  int get remainingUsage => isSubscribed ? -1 : (5 - usageCount).clamp(0, 5);
}
