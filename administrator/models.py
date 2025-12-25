"""
管理者系統 (AS) - 管理相關模型
根據 FOMO 系統需求規格書建立
"""
from django.db import models
from django.contrib.auth.models import User


class AdministratorProfile(models.Model):
    """管理者資料"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile', verbose_name="使用者")
    department = models.CharField(max_length=100, blank=True, verbose_name="部門")
    phone = models.CharField(max_length=20, blank=True, verbose_name="電話")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    
    class Meta:
        verbose_name = "管理者資料"
        verbose_name_plural = "管理者資料"
    
    def __str__(self):
        return f"{self.user.username} (管理者)"


class SystemLog(models.Model):
    """系統日誌"""
    ACTION_CHOICES = [
        ('create', '建立'),
        ('update', '更新'),
        ('delete', '刪除'),
        ('login', '登入'),
        ('logout', '登出'),
        ('payment', '支付'),
        ('refund', '退款'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="使用者")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="操作")
    model_name = models.CharField(max_length=100, verbose_name="模型名稱")
    object_id = models.CharField(max_length=100, blank=True, verbose_name="物件ID")
    description = models.TextField(verbose_name="描述")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP位址")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    
    class Meta:
        verbose_name = "系統日誌"
        verbose_name_plural = "系統日誌"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} - {self.model_name} - {self.created_at}"
