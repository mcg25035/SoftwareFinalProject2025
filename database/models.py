"""
資料庫系統 (DBS) - 核心資料模型
根據 FOMO 系統需求規格書建立
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Category(models.Model):
    """商品分類"""
    name = models.CharField(max_length=100, verbose_name="分類名稱")
    description = models.TextField(blank=True, verbose_name="分類描述")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children', verbose_name="父分類")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    class Meta:
        verbose_name = "商品分類"
        verbose_name_plural = "商品分類"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """商品模型"""
    STATUS_CHOICES = [
        ('active', '上架中'),
        ('inactive', '下架'),
        ('out_of_stock', '缺貨'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="商品名稱")
    description = models.TextField(verbose_name="商品描述")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name="分類")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="價格")
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="庫存數量")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="狀態")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="商品圖片")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    view_count = models.IntegerField(default=0, verbose_name="瀏覽次數")
    
    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        """計算平均評分"""
        ratings = self.reviews.all()
        if ratings.exists():
            return sum(r.rating for r in ratings) / ratings.count()
        return 0


class ProductImage(models.Model):
    """商品圖片"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="商品")
    image = models.ImageField(upload_to='products/', verbose_name="圖片")
    is_primary = models.BooleanField(default=False, verbose_name="主要圖片")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    
    class Meta:
        verbose_name = "商品圖片"
        verbose_name_plural = "商品圖片"
    
    def __str__(self):
        return f"{self.product.name} - 圖片"


class CustomerProfile(models.Model):
    """顧客個人資料擴展"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', verbose_name="使用者")
    phone = models.CharField(max_length=20, blank=True, verbose_name="電話")
    address = models.TextField(blank=True, verbose_name="地址")
    birth_date = models.DateField(null=True, blank=True, verbose_name="生日")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="頭像")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    class Meta:
        verbose_name = "顧客資料"
        verbose_name_plural = "顧客資料"
    
    def __str__(self):
        return f"{self.user.username} 的資料"


class ShoppingCart(models.Model):
    """購物車"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_cart', verbose_name="使用者")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="數量")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="加入時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    class Meta:
        verbose_name = "購物車"
        verbose_name_plural = "購物車"
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} x{self.quantity}"
    
    @property
    def subtotal(self):
        """小計"""
        return self.product.price * self.quantity


class Order(models.Model):
    """訂單"""
    STATUS_CHOICES = [
        ('pending', '待付款'),
        ('paid', '已付款'),
        ('processing', '處理中'),
        ('shipped', '已出貨'),
        ('delivered', '已送達'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="使用者")
    order_number = models.CharField(max_length=50, unique=True, verbose_name="訂單編號")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="狀態")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="總金額")
    shipping_address = models.TextField(verbose_name="配送地址")
    shipping_phone = models.CharField(max_length=20, verbose_name="配送電話")
    notes = models.TextField(blank=True, verbose_name="備註")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    class Meta:
        verbose_name = "訂單"
        verbose_name_plural = "訂單"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"訂單 {self.order_number}"


class OrderItem(models.Model):
    """訂單項目"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="訂單")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="數量")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="單價")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="小計")
    
    class Meta:
        verbose_name = "訂單項目"
        verbose_name_plural = "訂單項目"
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product.name}"


class ProductReview(models.Model):
    """商品評價"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="商品")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="使用者")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="評分")
    comment = models.TextField(verbose_name="評論")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    class Meta:
        verbose_name = "商品評價"
        verbose_name_plural = "商品評價"
        unique_together = ['product', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} 對 {self.product.name} 的評價"


class Favorite(models.Model):
    """商品收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name="使用者")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by', verbose_name="商品")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏時間")
    
    class Meta:
        verbose_name = "收藏"
        verbose_name_plural = "收藏"
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} 收藏了 {self.product.name}"


class Notification(models.Model):
    """通知"""
    TYPE_CHOICES = [
        ('order', '訂單通知'),
        ('payment', '付款通知'),
        ('promotion', '促銷通知'),
        ('system', '系統通知'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="使用者")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="類型")
    title = models.CharField(max_length=200, verbose_name="標題")
    message = models.TextField(verbose_name="訊息")
    is_read = models.BooleanField(default=False, verbose_name="已讀")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    
    class Meta:
        verbose_name = "通知"
        verbose_name_plural = "通知"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Coupon(models.Model):
    """優惠券"""
    code = models.CharField(max_length=50, unique=True, verbose_name="優惠碼")
    description = models.TextField(verbose_name="描述")
    discount_type = models.CharField(max_length=20, choices=[('percentage', '百分比'), ('fixed', '固定金額')], verbose_name="折扣類型")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="折扣值")
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="最低消費")
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="最高折扣")
    valid_from = models.DateTimeField(verbose_name="有效開始時間")
    valid_until = models.DateTimeField(verbose_name="有效結束時間")
    usage_limit = models.IntegerField(null=True, blank=True, verbose_name="使用次數限制")
    used_count = models.IntegerField(default=0, verbose_name="已使用次數")
    is_active = models.BooleanField(default=True, verbose_name="啟用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    
    class Meta:
        verbose_name = "優惠券"
        verbose_name_plural = "優惠券"
    
    def __str__(self):
        return self.code


class ProductQuestion(models.Model):
    """商品問答"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions', verbose_name="商品")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', verbose_name="提問者")
    question = models.TextField(verbose_name="問題")
    answer = models.TextField(blank=True, verbose_name="回答")
    answered_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='answered_questions', verbose_name="回答者")
    answered_at = models.DateTimeField(null=True, blank=True, verbose_name="回答時間")
    is_public = models.BooleanField(default=True, verbose_name="公開")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="提問時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    class Meta:
        verbose_name = "商品問答"
        verbose_name_plural = "商品問答"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.question[:50]}"


class ProductTracking(models.Model):
    """商品追蹤"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracked_products', verbose_name="使用者")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='tracked_by', verbose_name="商品")
    track_price = models.BooleanField(default=True, verbose_name="追蹤價格")
    track_stock = models.BooleanField(default=True, verbose_name="追蹤庫存")
    track_status = models.BooleanField(default=True, verbose_name="追蹤狀態")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    
    class Meta:
        verbose_name = "商品追蹤"
        verbose_name_plural = "商品追蹤"
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} 追蹤 {self.product.name}"


class ProductPriceHistory(models.Model):
    """商品價格歷史"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history', verbose_name="商品")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="價格")
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name="變動時間")
    
    class Meta:
        verbose_name = "商品價格歷史"
        verbose_name_plural = "商品價格歷史"
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.price} ({self.changed_at})"
