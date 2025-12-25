"""
資料庫信號處理器
用於自動追蹤商品價格變動
"""
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Product, ProductPriceHistory, ProductTracking, Notification


@receiver(pre_save, sender=Product)
def track_price_change(sender, instance, **kwargs):
    """追蹤商品價格變動"""
    if instance.pk:  # 更新現有商品
        try:
            old_product = Product.objects.get(pk=instance.pk)
            if old_product.price != instance.price:
                # 記錄價格歷史
                ProductPriceHistory.objects.create(
                    product=instance,
                    price=instance.price
                )
                
                # 通知追蹤此商品的顧客
                trackings = ProductTracking.objects.filter(
                    product=instance,
                    track_price=True
                )
                
                for tracking in trackings:
                    Notification.objects.create(
                        user=tracking.user,
                        type='promotion',
                        title='商品價格變動',
                        message=f'您追蹤的商品 {instance.name} 價格已變動為 NT$ {instance.price}'
                    )
        except Product.DoesNotExist:
            pass

