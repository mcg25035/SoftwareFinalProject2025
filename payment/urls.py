from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('methods/', views.payment_methods, name='payment_methods'),
    path('process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('transaction/<int:transaction_id>/', views.payment_detail, name='payment_detail'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('refund/<int:order_id>/', views.request_refund, name='request_refund'),
    path('refund/detail/<int:refund_id>/', views.refund_detail, name='refund_detail'),
    path('refunds/', views.refund_list, name='refund_list'),
    
    # 客服功能
    path('faq/', views.faq_list, name='faq_list'),
    path('ticket/create/', views.create_ticket, name='create_ticket'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    
    # 付款帳號管理
    path('accounts/', views.payment_accounts, name='payment_accounts'),
    path('accounts/add/', views.add_payment_account, name='add_payment_account'),
    path('accounts/<int:account_id>/set-default/', views.set_default_account, name='set_default_account'),
    path('accounts/<int:account_id>/delete/', views.delete_payment_account, name='delete_payment_account'),
]

