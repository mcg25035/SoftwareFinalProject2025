"""
初始化 FOMO 系統資料
"""
from django.core.management.base import BaseCommand
from payment.models import PaymentMethod
from database.models import Category


class Command(BaseCommand):
    help = '初始化 FOMO 系統的基礎資料'

    def handle(self, *args, **options):
        # 建立付款方式
        payment_methods = [
            {'name': '信用卡', 'code': 'credit_card', 'description': '使用信用卡付款'},
            {'name': '銀行轉帳', 'code': 'bank_transfer', 'description': 'ATM 或網路銀行轉帳'},
            {'name': '貨到付款', 'code': 'cod', 'description': '商品送達時付款'},
        ]
        
        for method_data in payment_methods:
            PaymentMethod.objects.get_or_create(
                code=method_data['code'],
                defaults=method_data
            )
            self.stdout.write(self.style.SUCCESS(f'已建立付款方式: {method_data["name"]}'))
        
        # 建立商品分類
        categories = [
            {'name': '電子產品', 'description': '各種電子產品'},
            {'name': '服飾配件', 'description': '服裝與配件'},
            {'name': '食品飲料', 'description': '食品與飲料'},
            {'name': '居家生活', 'description': '居家用品'},
            {'name': '運動休閒', 'description': '運動與休閒用品'},
        ]
        
        for cat_data in categories:
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            self.stdout.write(self.style.SUCCESS(f'已建立分類: {cat_data["name"]}'))
        
        self.stdout.write(self.style.SUCCESS('初始化完成！'))

