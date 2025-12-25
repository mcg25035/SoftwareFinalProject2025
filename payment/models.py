"""
金流系統 (PS) - 支付相關模型
根據 FOMO 系統需求規格書建立
"""
from django.db import models
from django.contrib.auth.models import User
from database.models import Order
from decimal import Decimal


class PaymentMethod(models.Model):
    """付款方式"""
    name = models.CharField(max_length=50, verbose_name="付款方式名稱")
    code = models.CharField(max_length=20, unique=True, verbose_name="代碼")
    is_active = models.BooleanField(default=True, verbose_name="啟用")
    description = models.TextField(blank=True, verbose_name="描述")
    
    class Meta:
        verbose_name = "付款方式"
        verbose_name_plural = "付款方式"
    
    def __str__(self):
        return self.name


class PaymentTransaction(models.Model):
    """支付交易記錄"""
    STATUS_CHOICES = [
        ('pending', '待處理'),
        ('processing', '處理中'),
        ('completed', '已完成'),
        ('failed', '失敗'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name="訂單")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_transactions', verbose_name="使用者")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, verbose_name="付款方式")
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name="交易編號")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="金額")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="狀態")
    payment_data = models.JSONField(null=True, blank=True, verbose_name="支付資料")
    response_data = models.JSONField(null=True, blank=True, verbose_name="回應資料")
    error_message = models.TextField(blank=True, verbose_name="錯誤訊息")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成時間")
    
    class Meta:
        verbose_name = "支付交易"
        verbose_name_plural = "支付交易"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"交易 {self.transaction_id} - {self.amount}"


class Refund(models.Model):
    """退款記錄"""
    STATUS_CHOICES = [
        ('pending', '待處理'),
        ('processing', '處理中'),
        ('completed', '已完成'),
        ('rejected', '已拒絕'),
    ]
    
    payment_transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name='refunds', verbose_name="支付交易")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds', verbose_name="訂單")
    refund_id = models.CharField(max_length=100, unique=True, verbose_name="退款編號")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="退款金額")
    reason = models.TextField(verbose_name="退款原因")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="狀態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成時間")
    
    class Meta:
        verbose_name = "退款"
        verbose_name_plural = "退款"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"退款 {self.refund_id} - {self.amount}"


class CustomerServiceTicket(models.Model):
    """客服工單"""
    STATUS_CHOICES = [
        ('open', '開啟'),
        ('in_progress', '處理中'),
        ('resolved', '已解決'),
        ('closed', '已關閉'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '緊急'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_tickets', verbose_name="使用者")
    subject = models.CharField(max_length=200, verbose_name="主旨")
    description = models.TextField(verbose_name="問題描述")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="狀態")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="優先級")
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tickets', verbose_name="指派給")
    related_order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL, related_name='service_tickets', verbose_name="相關訂單")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="解決時間")
    
    class Meta:
        verbose_name = "客服工單"
        verbose_name_plural = "客服工單"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"工單 #{self.id} - {self.subject}"


class CustomerServiceMessage(models.Model):
    """客服訊息"""
    ticket = models.ForeignKey(CustomerServiceTicket, on_delete=models.CASCADE, related_name='messages', verbose_name="工單")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="發送者")
    message = models.TextField(verbose_name="訊息內容")
    is_from_staff = models.BooleanField(default=False, verbose_name="來自客服")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="發送時間")
    
    class Meta:
        verbose_name = "客服訊息"
        verbose_name_plural = "客服訊息"
        ordering = ['created_at']
    
    def __str__(self):
        return f"工單 #{self.ticket.id} - {self.message[:50]}"


class FAQ(models.Model):
    """常見問題"""
    CATEGORY_CHOICES = [
        ('payment', '付款相關'),
        ('order', '訂單相關'),
        ('refund', '退款相關'),
        ('product', '商品相關'),
        ('account', '帳號相關'),
        ('other', '其他'),
    ]
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="分類")
    question = models.CharField(max_length=200, verbose_name="問題")
    answer = models.TextField(verbose_name="回答")
    order = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="啟用")
    view_count = models.IntegerField(default=0, verbose_name="瀏覽次數")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    class Meta:
        verbose_name = "常見問題"
        verbose_name_plural = "常見問題"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.question


class PaymentAccount(models.Model):
    """付款帳號"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_accounts', verbose_name="使用者")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name="付款方式")
    account_name = models.CharField(max_length=100, verbose_name="帳號名稱")
    account_info = models.JSONField(verbose_name="帳號資訊")  # 加密儲存
    is_default = models.BooleanField(default=False, verbose_name="預設")
    is_active = models.BooleanField(default=True, verbose_name="啟用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    class Meta:
        verbose_name = "付款帳號"
        verbose_name_plural = "付款帳號"
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.account_name}"
