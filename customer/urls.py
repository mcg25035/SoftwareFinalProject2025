from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    # 商品相關
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    
    # 購物車
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # 結帳與訂單
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # 個人資料
    path('profile/', views.profile, name='profile'),
    
    # 評價
    path('products/<int:product_id>/review/', views.add_review, name='add_review'),
    
    # 收藏
    path('products/<int:product_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_list, name='favorite_list'),
    
    # 通知
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # 商品問答
    path('products/<int:product_id>/question/', views.ask_question, name='ask_question'),
    
    # 商品追蹤
    path('products/<int:product_id>/track/', views.track_product, name='track_product'),
    path('products/<int:product_id>/untrack/', views.untrack_product, name='untrack_product'),
    path('tracked/', views.tracked_products, name='tracked_products'),
]

