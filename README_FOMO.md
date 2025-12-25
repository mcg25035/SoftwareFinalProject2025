# FOMO 線上購物網站系統

根據系統需求規格書實作的完整電子商務平台。

## 系統架構

本系統包含以下四個子系統：

### 1. 資料庫系統 (DBS)
- 核心資料模型：商品、分類、訂單、購物車、評價、收藏等
- 資料庫管理與維護

### 2. 顧客系統 (CS)
- 商品瀏覽與搜尋
- 購物車管理
- 訂單管理
- 個人資料管理
- 商品收藏與追蹤
- 商品評價
- 通知中心

### 3. 金流系統 (PS)
- 支付處理
- 交易記錄查詢
- 退款申請與處理
- 金流通知

### 4. 管理者系統 (AS)
- 商品管理（新增、編輯、刪除）
- 訂單管理
- 退款管理
- 使用者管理
- 系統日誌

## 安裝與設定

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 資料庫遷移
```bash
python manage.py migrate
```

### 3. 初始化基礎資料
```bash
python manage.py init_fomo_data
```

此命令會建立：
- 付款方式（信用卡、銀行轉帳、貨到付款）
- 商品分類（電子產品、服飾配件、食品飲料等）

### 4. 建立超級使用者（管理者）
```bash
python manage.py createsuperuser
```

### 5. 啟動開發伺服器
```bash
python manage.py runserver
```

## 使用說明

### 顧客功能
1. 訪問 `http://localhost:8000/customer/products/` 瀏覽商品
2. 註冊/登入帳號
3. 將商品加入購物車
4. 結帳並完成付款
5. 查看訂單狀態
6. 評價商品
7. 收藏喜歡的商品

### 管理者功能
1. 使用超級使用者帳號登入
2. 訪問 `http://localhost:8000/administrator/dashboard/` 進入管理後台
3. 管理商品、訂單、退款等

## URL 路由

### 顧客系統
- `/customer/products/` - 商品列表
- `/customer/products/<id>/` - 商品詳情
- `/customer/cart/` - 購物車
- `/customer/checkout/` - 結帳
- `/customer/orders/` - 訂單列表
- `/customer/profile/` - 個人資料
- `/customer/favorites/` - 收藏列表
- `/customer/notifications/` - 通知中心

### 金流系統
- `/payment/process/<order_id>/` - 處理付款
- `/payment/transactions/` - 交易記錄
- `/payment/refund/<order_id>/` - 申請退款

### 管理者系統
- `/administrator/dashboard/` - 管理後台首頁
- `/administrator/products/` - 商品管理
- `/administrator/orders/` - 訂單管理
- `/administrator/refunds/` - 退款管理
- `/administrator/users/` - 使用者管理
- `/administrator/logs/` - 系統日誌

## 資料模型

### 核心模型
- `Product` - 商品
- `Category` - 商品分類
- `Order` - 訂單
- `OrderItem` - 訂單項目
- `ShoppingCart` - 購物車
- `ProductReview` - 商品評價
- `Favorite` - 收藏
- `Notification` - 通知
- `Coupon` - 優惠券

### 支付模型
- `PaymentMethod` - 付款方式
- `PaymentTransaction` - 支付交易
- `Refund` - 退款

### 管理模型
- `AdministratorProfile` - 管理者資料
- `SystemLog` - 系統日誌

## 安全功能

- 使用者認證與授權
- CSRF 保護
- 權限控制（管理者/顧客）
- 系統操作日誌記錄

## 開發注意事項

1. 支付功能目前為模擬實作，實際部署時需整合第三方支付 API
2. 圖片上傳功能需要設定 MEDIA_ROOT 和 MEDIA_URL
3. 生產環境請修改 SECRET_KEY 並關閉 DEBUG 模式

## 技術棧

- Django 5.2.1
- Bootstrap 5.3.0
- SQLite（開發環境）

## 授權

本專案為學術用途，根據 FOMO 系統需求規格書實作。

