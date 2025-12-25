from django.contrib import admin
from .models import (
    Category, Product, ProductImage, CustomerProfile,
    ShoppingCart, Order, OrderItem, ProductReview,
    Favorite, Notification, Coupon, ProductQuestion,
    ProductTracking, ProductPriceHistory
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    prepopulated_fields = {'name': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'status', 'view_count', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['view_count', 'created_at', 'updated_at']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__username', 'phone']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username']
    readonly_fields = ['order_number', 'created_at', 'updated_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'subtotal']
    list_filter = ['order__status']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'title', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_until']
    list_filter = ['is_active', 'discount_type', 'valid_from']
    search_fields = ['code']


@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'question', 'is_answered', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at', 'answered_at']
    search_fields = ['question', 'product__name', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'answered_at']
    
    def is_answered(self, obj):
        return bool(obj.answer)
    is_answered.boolean = True
    is_answered.short_description = '已回答'


@admin.register(ProductTracking)
class ProductTrackingAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'track_price', 'track_stock', 'track_status', 'created_at']
    list_filter = ['track_price', 'track_stock', 'track_status', 'created_at']
    search_fields = ['user__username', 'product__name']


@admin.register(ProductPriceHistory)
class ProductPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'changed_at']
    list_filter = ['changed_at']
    search_fields = ['product__name']
    readonly_fields = ['changed_at']
