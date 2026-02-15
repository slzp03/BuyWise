import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../services/supabase_service.dart';
import '../models/purchase.dart';
import '../l10n/translations.dart';
import '../widgets/purchase_form.dart';
import '../widgets/purchase_list.dart';

/// 가계부 화면 (app.py expense_tracker() 대응)
class ExpenseTrackerScreen extends StatefulWidget {
  const ExpenseTrackerScreen({super.key});

  @override
  State<ExpenseTrackerScreen> createState() => _ExpenseTrackerScreenState();
}

class _ExpenseTrackerScreenState extends State<ExpenseTrackerScreen> {
  List<Purchase> _purchases = [];
  Set<int> _selectedIds = {};
  bool _isLoading = false;
  String _periodFilter = 'all';

  @override
  void initState() {
    super.initState();
    _loadPurchases();
  }

  String get _lang {
    final auth = context.read<AuthService>();
    return auth.currentUser?.language ?? 'ko';
  }

  String? get _userId {
    return context.read<AuthService>().currentUser?.id;
  }

  /// 기간 필터에 따른 시작 날짜
  String? get _dateFrom {
    final now = DateTime.now();
    switch (_periodFilter) {
      case '1m':
        return DateFormat('yyyy-MM-dd')
            .format(DateTime(now.year, now.month - 1, now.day));
      case '3m':
        return DateFormat('yyyy-MM-dd')
            .format(DateTime(now.year, now.month - 3, now.day));
      case '6m':
        return DateFormat('yyyy-MM-dd')
            .format(DateTime(now.year, now.month - 6, now.day));
      default:
        return null;
    }
  }

  Future<void> _loadPurchases() async {
    if (_userId == null) return;

    setState(() => _isLoading = true);

    final purchases = await SupabaseService.instance.loadPurchases(
      _userId!,
      dateFrom: _dateFrom,
    );

    setState(() {
      _purchases = purchases;
      _selectedIds = {};
      _isLoading = false;
    });
  }

  Future<void> _savePurchase(Purchase purchase) async {
    if (_userId == null) return;

    final success =
        await SupabaseService.instance.saveSinglePurchase(_userId!, purchase);

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(AppTranslations.t('purchase_saved', lang: _lang)),
          backgroundColor: Colors.green,
        ),
      );
      _loadPurchases();
    }
  }

  Future<void> _deleteSelected() async {
    if (_userId == null || _selectedIds.isEmpty) return;

    final success = await SupabaseService.instance.deletePurchases(
      _userId!,
      _selectedIds.toList(),
    );

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
              '${_selectedIds.length}${AppTranslations.t('purchases_deleted', lang: _lang)}'),
        ),
      );
      _loadPurchases();
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = _lang;

    return Scaffold(
      appBar: AppBar(
        title: Text(AppTranslations.t('expense_tracker', lang: lang)),
        actions: [
          // 총 기록 수
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(
              child: Text(
                '${AppTranslations.t('total_records', lang: lang)}: ${_purchases.length}',
                style: TextStyle(fontSize: 13, color: Colors.grey[600]),
              ),
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadPurchases,
        child: CustomScrollView(
          slivers: [
            // 빠른 기록 폼
            SliverToBoxAdapter(
              child: PurchaseForm(
                lang: lang,
                onSave: _savePurchase,
              ),
            ),

            // 기간 필터
            SliverToBoxAdapter(
              child: _buildPeriodFilter(lang),
            ),

            // 구매 이력 목록
            if (_isLoading)
              const SliverFillRemaining(
                child: Center(child: CircularProgressIndicator()),
              )
            else if (_purchases.isEmpty)
              SliverFillRemaining(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.receipt_long,
                          size: 64, color: Colors.grey[300]),
                      const SizedBox(height: 16),
                      Text(
                        AppTranslations.t('no_purchases_yet', lang: lang),
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey[500]),
                      ),
                    ],
                  ),
                ),
              )
            else
              SliverToBoxAdapter(
                child: PurchaseList(
                  purchases: _purchases,
                  selectedIds: _selectedIds,
                  lang: lang,
                  onSelectionChanged: (ids) {
                    setState(() => _selectedIds = ids);
                  },
                ),
              ),
          ],
        ),
      ),

      // 하단 버튼
      bottomSheet: _selectedIds.isNotEmpty
          ? Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              color: Colors.red[50],
              child: ElevatedButton.icon(
                onPressed: _deleteSelected,
                icon: const Icon(Icons.delete_outline),
                label: Text(
                  '${AppTranslations.t('delete_selected', lang: lang)} (${_selectedIds.length})',
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
              ),
            )
          : null,
    );
  }

  Widget _buildPeriodFilter(String lang) {
    final filters = [
      ('all', AppTranslations.t('period_all', lang: lang)),
      ('1m', AppTranslations.t('period_1m', lang: lang)),
      ('3m', AppTranslations.t('period_3m', lang: lang)),
      ('6m', AppTranslations.t('period_6m', lang: lang)),
    ];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          Icon(Icons.filter_list, size: 18, color: Colors.grey[600]),
          const SizedBox(width: 8),
          Text(
            AppTranslations.t('period_filter', lang: lang),
            style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: Colors.grey[700]),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: filters.map((filter) {
                  final isSelected = _periodFilter == filter.$1;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      label: Text(filter.$2,
                          style: const TextStyle(fontSize: 12)),
                      selected: isSelected,
                      onSelected: (_) {
                        setState(() => _periodFilter = filter.$1);
                        _loadPurchases();
                      },
                      visualDensity: VisualDensity.compact,
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
