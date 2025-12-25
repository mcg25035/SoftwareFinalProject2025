from django.contrib import admin
from .models import PaymentMethod, PaymentTransaction, Refund, CustomerServiceTicket, CustomerServiceMessage, FAQ, PaymentAccount


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'user', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'order__order_number', 'user__username']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at', 'completed_at']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['refund_id', 'payment_transaction', 'order', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['refund_id', 'order__order_number']
    readonly_fields = ['refund_id', 'created_at', 'updated_at', 'completed_at']


@admin.register(CustomerServiceTicket)
class CustomerServiceTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'status', 'priority', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['subject', 'user__username', 'description']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']


@admin.register(CustomerServiceMessage)
class CustomerServiceMessageAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'user', 'is_from_staff', 'created_at']
    list_filter = ['is_from_staff', 'created_at']
    search_fields = ['message', 'ticket__subject']
    readonly_fields = ['created_at']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'view_count', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    readonly_fields = ['view_count', 'created_at', 'updated_at']


@admin.register(PaymentAccount)
class PaymentAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_method', 'account_name', 'is_default', 'is_active', 'created_at']
    list_filter = ['payment_method', 'is_default', 'is_active', 'created_at']
    search_fields = ['user__username', 'account_name']
    readonly_fields = ['created_at', 'updated_at']
