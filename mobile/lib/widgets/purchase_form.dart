import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/purchase.dart';
import '../l10n/translations.dart';

/// 빠른 지출 기록 폼 위젯
class PurchaseForm extends StatefulWidget {
  final String lang;
  final Function(Purchase) onSave;

  const PurchaseForm({
    super.key,
    required this.lang,
    required this.onSave,
  });

  @override
  State<PurchaseForm> createState() => _PurchaseFormState();
}

class _PurchaseFormState extends State<PurchaseForm> {
  final _formKey = GlobalKey<FormState>();
  final _productController = TextEditingController();
  final _amountController = TextEditingController();
  final _customCategoryController = TextEditingController();

  String _category = '';
  bool _useCustomCategory = false;
  DateTime _purchaseDate = DateTime.now();
  int _thinkingDays = 0;
  bool _repurchaseIntent = true;
  int _usageFrequency = 3;
  bool _isExpanded = false;

  @override
  void dispose() {
    _productController.dispose();
    _amountController.dispose();
    _customCategoryController.dispose();
    super.dispose();
  }

  int get _autoNecessity {
    return Purchase.calculateNecessity(
      thinkingDays: _thinkingDays,
      repurchaseIntent: _repurchaseIntent,
    );
  }

  List<String> get _categories => AppTranslations.categories(widget.lang);

  void _save() {
    if (!_formKey.currentState!.validate()) return;

    final category = _useCustomCategory
        ? _customCategoryController.text.trim()
        : _category;

    if (category.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
              AppTranslations.t('input_error_category', lang: widget.lang)),
        ),
      );
      return;
    }

    final purchase = Purchase(
      purchaseDate: _purchaseDate,
      category: category,
      productName: _productController.text.trim(),
      amount: double.parse(_amountController.text),
      necessityScore: _autoNecessity,
      usageFrequency: _usageFrequency,
      thinkingDays: _thinkingDays,
      repurchaseIntent: _repurchaseIntent,
    );

    widget.onSave(purchase);

    // 폼 초기화
    _productController.clear();
    _amountController.clear();
    _customCategoryController.clear();
    setState(() {
      _thinkingDays = 0;
      _repurchaseIntent = true;
      _usageFrequency = 3;
      _purchaseDate = DateTime.now();
    });
  }

  @override
  Widget build(BuildContext context) {
    final lang = widget.lang;

    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 헤더
              InkWell(
                onTap: () => setState(() => _isExpanded = !_isExpanded),
                child: Row(
                  children: [
                    const Icon(Icons.add_circle,
                        color: Color(0xFF6366F1), size: 22),
                    const SizedBox(width: 8),
                    Text(
                      AppTranslations.t('quick_add', lang: lang),
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const Spacer(),
                    Icon(
                      _isExpanded
                          ? Icons.expand_less
                          : Icons.expand_more,
                      color: Colors.grey[600],
                    ),
                  ],
                ),
              ),

              if (_isExpanded) ...[
                const SizedBox(height: 16),

                // 상품명
                TextFormField(
                  controller: _productController,
                  decoration: InputDecoration(
                    labelText: AppTranslations.t('product_name', lang: lang),
                    hintText:
                        AppTranslations.t('product_placeholder', lang: lang),
                    prefixIcon: const Icon(Icons.shopping_cart_outlined),
                  ),
                  validator: (v) => v == null || v.trim().isEmpty
                      ? AppTranslations.t('input_error_product', lang: lang)
                      : null,
                ),
                const SizedBox(height: 12),

                // 금액
                TextFormField(
                  controller: _amountController,
                  decoration: InputDecoration(
                    labelText: AppTranslations.t('amount', lang: lang),
                    prefixIcon: const Icon(Icons.payments_outlined),
                  ),
                  keyboardType: TextInputType.number,
                  validator: (v) {
                    if (v == null || v.isEmpty) return null;
                    final n = double.tryParse(v);
                    if (n == null || n <= 0) {
                      return AppTranslations.t(
                          'input_error_amount', lang: lang);
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 12),

                // 카테고리
                Row(
                  children: [
                    Expanded(
                      child: _useCustomCategory
                          ? TextFormField(
                              controller: _customCategoryController,
                              decoration: InputDecoration(
                                labelText: AppTranslations.t(
                                    'category_custom', lang: lang),
                                prefixIcon:
                                    const Icon(Icons.edit_outlined),
                              ),
                            )
                          : DropdownButtonFormField<String>(
                              value:
                                  _category.isEmpty ? null : _category,
                              decoration: InputDecoration(
                                labelText: AppTranslations.t(
                                    'category', lang: lang),
                                prefixIcon:
                                    const Icon(Icons.category_outlined),
                              ),
                              items: _categories
                                  .map((c) => DropdownMenuItem(
                                      value: c, child: Text(c)))
                                  .toList(),
                              onChanged: (v) =>
                                  setState(() => _category = v ?? ''),
                            ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      icon: Icon(
                        _useCustomCategory
                            ? Icons.list
                            : Icons.edit,
                        color: Colors.grey[600],
                      ),
                      onPressed: () => setState(
                          () => _useCustomCategory = !_useCustomCategory),
                      tooltip: AppTranslations.t(
                          'category_custom', lang: lang),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // 구매 날짜
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.calendar_today_outlined),
                  title: Text(AppTranslations.t(
                      'purchase_date', lang: lang)),
                  subtitle: Text(
                      DateFormat('yyyy-MM-dd').format(_purchaseDate)),
                  onTap: () async {
                    final date = await showDatePicker(
                      context: context,
                      initialDate: _purchaseDate,
                      firstDate: DateTime(2020),
                      lastDate: DateTime.now(),
                    );
                    if (date != null) {
                      setState(() => _purchaseDate = date);
                    }
                  },
                ),

                // 고민 기간
                Row(
                  children: [
                    const Icon(Icons.timer_outlined,
                        color: Colors.grey),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${AppTranslations.t('thinking_days', lang: lang)}: $_thinkingDays',
                            style: const TextStyle(fontSize: 13),
                          ),
                          Slider(
                            value: _thinkingDays.toDouble(),
                            min: 0,
                            max: 30,
                            divisions: 30,
                            label: '$_thinkingDays',
                            onChanged: (v) => setState(
                                () => _thinkingDays = v.toInt()),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),

                // 재구매 의향
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(
                    AppTranslations.t('repurchase', lang: lang),
                    style: const TextStyle(fontSize: 14),
                  ),
                  subtitle: Text(
                    _repurchaseIntent
                        ? AppTranslations.t('repurchase_yes', lang: lang)
                        : AppTranslations.t('repurchase_no', lang: lang),
                    style: const TextStyle(fontSize: 12),
                  ),
                  value: _repurchaseIntent,
                  onChanged: (v) =>
                      setState(() => _repurchaseIntent = v),
                ),

                // 사용빈도
                Row(
                  children: [
                    const Icon(Icons.repeat_outlined,
                        color: Colors.grey),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${AppTranslations.t('usage_freq', lang: lang)}: $_usageFrequency/5',
                            style: const TextStyle(fontSize: 13),
                          ),
                          Slider(
                            value: _usageFrequency.toDouble(),
                            min: 1,
                            max: 5,
                            divisions: 4,
                            label: '$_usageFrequency',
                            onChanged: (v) => setState(
                                () => _usageFrequency = v.toInt()),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),

                // 자동 계산 필요도 표시
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.indigo[50],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.auto_awesome,
                          size: 18, color: Color(0xFF6366F1)),
                      const SizedBox(width: 8),
                      Text(
                        '${AppTranslations.t('necessity_auto', lang: lang)}: $_autoNecessity/5',
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                          color: Color(0xFF6366F1),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '(${AppTranslations.t('necessity_$_autoNecessity', lang: lang)})',
                        style: TextStyle(
                            fontSize: 12, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // 저장 버튼
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _save,
                    icon: const Icon(Icons.save),
                    label: Text(
                        AppTranslations.t('btn_save', lang: lang)),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF6366F1),
                      foregroundColor: Colors.white,
                      padding:
                          const EdgeInsets.symmetric(vertical: 14),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
