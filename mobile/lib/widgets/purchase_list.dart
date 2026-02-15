import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/purchase.dart';
import '../services/regret_calculator.dart';

/// 구매 이력 목록 위젯
class PurchaseList extends StatelessWidget {
  final List<Purchase> purchases;
  final Set<int> selectedIds;
  final String lang;
  final Function(Set<int>) onSelectionChanged;

  const PurchaseList({
    super.key,
    required this.purchases,
    required this.selectedIds,
    required this.lang,
    required this.onSelectionChanged,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: purchases.length,
      itemBuilder: (context, index) {
        return _buildPurchaseItem(context, purchases[index]);
      },
    );
  }

  Widget _buildPurchaseItem(BuildContext context, Purchase purchase) {
    final id = purchase.id;
    final isSelected = id != null && selectedIds.contains(id);
    final dateStr =
        DateFormat('MM/dd').format(purchase.purchaseDate);

    // 후회 점수 색상
    final regretScore = purchase.regretScore ?? 0;
    final interp = RegretCalculator.interpret(regretScore);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      color: isSelected ? Colors.red[50] : null,
      child: InkWell(
        onTap: () {
          if (id == null) return;
          final newSet = Set<int>.from(selectedIds);
          if (isSelected) {
            newSet.remove(id);
          } else {
            newSet.add(id);
          }
          onSelectionChanged(newSet);
        },
        onLongPress: () {
          if (id == null) return;
          final newSet = Set<int>.from(selectedIds);
          if (isSelected) {
            newSet.remove(id);
          } else {
            newSet.add(id);
          }
          onSelectionChanged(newSet);
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              // 선택 체크박스
              if (selectedIds.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: Icon(
                    isSelected
                        ? Icons.check_circle
                        : Icons.circle_outlined,
                    color: isSelected ? Colors.red : Colors.grey[400],
                    size: 22,
                  ),
                ),

              // 카테고리 아이콘
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: Color(interp.color).withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Center(
                  child: Text(
                    _categoryEmoji(purchase.category),
                    style: const TextStyle(fontSize: 18),
                  ),
                ),
              ),
              const SizedBox(width: 12),

              // 상품 정보
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      purchase.productName.isNotEmpty
                          ? purchase.productName
                          : purchase.category,
                      style: const TextStyle(
                        fontWeight: FontWeight.w500,
                        fontSize: 14,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '$dateStr | ${purchase.category}',
                      style: TextStyle(
                          fontSize: 11, color: Colors.grey[500]),
                    ),
                  ],
                ),
              ),

              // 금액
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    _formatAmount(purchase.amount),
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  if (regretScore > 0)
                    Container(
                      margin: const EdgeInsets.only(top: 2),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 1),
                      decoration: BoxDecoration(
                        color:
                            Color(interp.color).withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${regretScore.toStringAsFixed(0)}점',
                        style: TextStyle(
                          fontSize: 10,
                          color: Color(interp.color),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _categoryEmoji(String category) {
    if (category.contains('전자') || category.contains('電子')) return '📱';
    if (category.contains('의류') || category.contains('衣類')) return '👕';
    if (category.contains('식비') || category.contains('食費')) return '🍔';
    if (category.contains('취미') || category.contains('趣味')) return '🎮';
    if (category.contains('미용') || category.contains('美容')) return '💄';
    if (category.contains('생활') || category.contains('生活')) return '🏠';
    if (category.contains('도서') || category.contains('書籍')) return '📚';
    if (category.contains('교육') || category.contains('教育')) return '🎓';
    if (category.contains('교통') || category.contains('交通')) return '🚗';
    return '📦';
  }

  String _formatAmount(double amount) {
    final formatter = NumberFormat('#,###');
    if (lang == 'ja') {
      return '¥${formatter.format(amount.toInt())}';
    }
    return '${formatter.format(amount.toInt())}원';
  }
}
