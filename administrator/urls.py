from django.urls import path
from . import views

app_name = 'administrator'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # 商品管理
    path('products/', views.product_management, name='product_management'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # 訂單管理
    path('orders/', views.order_management, name='order_management'),
    path('orders/<int:order_id>/', views.order_detail_admin, name='order_detail'),
    
    # 退款管理
    path('refunds/', views.refund_management, name='refund_management'),
    path('refunds/<int:refund_id>/process/', views.process_refund, name='process_refund'),
    
    # 使用者管理
    path('users/', views.user_management, name='user_management'),
    
    # 系統日誌
    path('logs/', views.system_logs, name='system_logs'),
    
    # 問答管理
    path('questions/', views.question_management, name='question_management'),
    path('questions/<int:question_id>/answer/', views.answer_question, name='answer_question'),
    
    # 客服管理
    path('tickets/', views.ticket_management, name='ticket_management'),
    path('tickets/<int:ticket_id>/', views.ticket_detail_admin, name='ticket_detail'),
    
    # FAQ 管理
    path('faqs/', views.faq_management, name='faq_management'),
    path('faqs/create/', views.faq_create, name='faq_create'),
    path('faqs/<int:faq_id>/edit/', views.faq_edit, name='faq_edit'),
    path('faqs/<int:faq_id>/delete/', views.faq_delete, name='faq_delete'),
]

