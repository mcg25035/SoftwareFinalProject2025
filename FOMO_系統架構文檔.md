# FOMO 線上購物網站系統 - 完整架構文檔

## 一、系統概述

### 1.1 系統簡介
FOMO (Fear Of Missing Out) 線上購物網站系統是一個完整的電子商務平台，根據 IEEE 830 與 ISO/IEC 25010 標準設計，提供完整的購物、支付、管理功能。

### 1.2 系統版本
- **主系統版本**: FOSWS 1.0.0
- **管理者系統**: AS 1.1.0
- **顧客系統**: CS 1.2.0
- **金流系統**: PS 1.4.0
- **資料庫系統**: DBS 1.4.0

### 1.3 技術棧
- **後端框架**: Django 5.2.1
- **資料庫**: SQLite (開發環境)
- **前端框架**: Bootstrap 5.3.0
- **圖標庫**: Bootstrap Icons
- **Python版本**: 3.12+

---

## 二、系統架構

### 2.1 整體架構圖

```
┌─────────────────────────────────────────────────────────┐
│                    FOMO 主系統 (FOSWS)                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  顧客系統    │  │  金流系統    │  │  管理者系統  │ │
│  │   (CS)       │  │   (PS)       │  │   (AS)       │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                  │                  │         │
│         └──────────────────┴──────────────────┘         │
│                          │                              │
│                          ▼                              │
│                  ┌──────────────┐                      │
│                  │  資料庫系統  │                      │
│                  │   (DBS)      │                      │
│                  └──────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### 2.2 子系統說明

#### 2.2.1 資料庫系統 (DBS)
**職責**: 核心資料模型與資料管理

**主要模型**:
- `Category` - 商品分類
- `Product` - 商品
- `ProductImage` - 商品圖片
- `CustomerProfile` - 顧客資料
- `ShoppingCart` - 購物車
- `Order` - 訂單
- `OrderItem` - 訂單項目
- `ProductReview` - 商品評價
- `Favorite` - 收藏
- `Notification` - 通知
- `Coupon` - 優惠券

**功能**:
- 資料持久化
- 資料關聯管理
- 資料驗證

#### 2.2.2 顧客系統 (CS)
**職責**: 提供顧客端所有功能

**主要功能模組**:
1. **商品瀏覽與搜尋**
   - 商品列表（分頁、分類、排序）
   - 商品詳情
   - 商品搜尋
   - 相關商品推薦

2. **購物車管理**
   - 加入購物車
   - 更新數量
   - 移除商品
   - 購物車總計

3. **訂單管理**
   - 建立訂單
   - 訂單列表
   - 訂單詳情
   - 訂單狀態追蹤

4. **個人資料管理**
   - 個人資料編輯
   - 頭像上傳
   - 地址管理

5. **互動功能**
   - 商品收藏
   - 商品評價
   - 通知中心

**URL 路由**:
```
/customer/products/              - 商品列表
/customer/products/<id>/         - 商品詳情
/customer/cart/                  - 購物車
/customer/cart/add/<id>/        - 加入購物車
/customer/cart/update/<id>/      - 更新購物車
/customer/cart/remove/<id>/      - 移除商品
/customer/checkout/              - 結帳
/customer/orders/                - 訂單列表
/customer/orders/<id>/          - 訂單詳情
/customer/profile/               - 個人資料
/customer/favorites/             - 收藏列表
/customer/notifications/         - 通知中心
```

#### 2.2.3 金流系統 (PS)
**職責**: 處理所有支付相關功能

**主要功能模組**:
1. **支付處理**
   - 多種付款方式支援
   - 支付交易記錄
   - 支付狀態管理

2. **退款管理**
   - 退款申請
   - 退款審核
   - 退款記錄

3. **交易查詢**
   - 交易歷史
   - 交易詳情
   - 交易狀態追蹤

**主要模型**:
- `PaymentMethod` - 付款方式
- `PaymentTransaction` - 支付交易
- `Refund` - 退款記錄

**URL 路由**:
```
/payment/methods/                    - 付款方式列表
/payment/process/<order_id>/         - 處理付款
/payment/transaction/<id>/          - 支付詳情
/payment/transactions/               - 交易記錄
/payment/refund/<order_id>/         - 申請退款
/payment/refund/detail/<id>/         - 退款詳情
/payment/refunds/                    - 退款列表
```

#### 2.2.4 管理者系統 (AS)
**職責**: 提供管理後台所有功能

**主要功能模組**:
1. **儀表板**
   - 統計資料展示
   - 今日訂單/營收
   - 待處理事項提醒
   - 熱門商品排行

2. **商品管理**
   - 商品新增
   - 商品編輯
   - 商品刪除
   - 商品狀態管理
   - 庫存管理

3. **訂單管理**
   - 訂單列表
   - 訂單詳情
   - 訂單狀態更新
   - 訂單搜尋

4. **退款管理**
   - 退款申請列表
   - 退款審核
   - 退款狀態管理

5. **使用者管理**
   - 使用者列表
   - 使用者資料查詢

6. **系統日誌**
   - 操作記錄
   - 系統事件追蹤
   - 日誌查詢與篩選

**主要模型**:
- `AdministratorProfile` - 管理者資料
- `SystemLog` - 系統日誌

**URL 路由**:
```
/administrator/dashboard/            - 管理後台首頁
/administrator/products/             - 商品管理
/administrator/products/create/     - 新增商品
/administrator/products/<id>/edit/   - 編輯商品
/administrator/products/<id>/delete/ - 刪除商品
/administrator/orders/               - 訂單管理
/administrator/orders/<id>/          - 訂單詳情
/administrator/refunds/              - 退款管理
/administrator/refunds/<id>/process/ - 處理退款
/administrator/users/                - 使用者管理
/administrator/logs/                 - 系統日誌
```

---

## 三、資料流程

### 3.1 購物流程

```
顧客瀏覽商品
    ↓
加入購物車
    ↓
前往結帳
    ↓
填寫配送資訊
    ↓
建立訂單 (狀態: pending)
    ↓
選擇付款方式
    ↓
處理支付 (狀態: processing → completed)
    ↓
更新訂單狀態 (狀態: paid)
    ↓
管理者處理訂單 (狀態: processing → shipped → delivered)
```

### 3.2 退款流程

```
顧客申請退款
    ↓
建立退款記錄 (狀態: pending)
    ↓
管理者審核
    ↓
核准/拒絕
    ↓
更新退款狀態 (completed/rejected)
    ↓
更新訂單狀態 (refunded)
    ↓
發送通知
```

### 3.3 評價流程

```
顧客購買商品
    ↓
訂單完成 (delivered)
    ↓
顧客評價商品
    ↓
檢查是否已購買
    ↓
建立/更新評價
    ↓
更新商品平均評分
```

---

## 四、資料模型關係圖

```
User (Django Auth)
    ├── CustomerProfile (1:1)
    ├── ShoppingCart (1:N)
    ├── Order (1:N)
    ├── ProductReview (1:N)
    ├── Favorite (1:N)
    ├── Notification (1:N)
    └── PaymentTransaction (1:N)

Product
    ├── Category (N:1)
    ├── ProductImage (1:N)
    ├── ShoppingCart (1:N)
    ├── OrderItem (1:N)
    ├── ProductReview (1:N)
    └── Favorite (1:N)

Order
    ├── User (N:1)
    ├── OrderItem (1:N)
    ├── PaymentTransaction (1:N)
    └── Refund (1:N)

PaymentTransaction
    ├── Order (N:1)
    ├── User (N:1)
    ├── PaymentMethod (N:1)
    └── Refund (1:N)
```

---

## 五、安全機制

### 5.1 認證與授權
- Django 內建認證系統
- 登入/登出功能
- 密碼加密儲存
- Session 管理

### 5.2 權限控制
- **顧客權限**: 只能存取自己的資料
- **管理者權限**: 使用 `@user_passes_test(is_admin)` 裝飾器
- **資料隔離**: 查詢時自動過濾使用者資料

### 5.3 CSRF 保護
- Django CSRF Middleware
- 所有 POST 請求都需要 CSRF Token

### 5.4 系統日誌
- 記錄所有重要操作
- 包含使用者、操作類型、IP 位址
- 用於審計與追蹤

---

## 六、頁面清單與功能檢查

### 6.1 顧客系統頁面

| 頁面 | URL | 功能 | 狀態 |
|------|-----|------|------|
| 商品列表 | `/customer/products/` | 商品瀏覽、搜尋、分類、排序 | ✅ |
| 商品詳情 | `/customer/products/<id>/` | 商品資訊、評價、收藏、加入購物車 | ✅ |
| 購物車 | `/customer/cart/` | 查看購物車、更新數量、移除商品 | ✅ |
| 結帳 | `/customer/checkout/` | 填寫配送資訊、使用優惠券 | ✅ |
| 訂單列表 | `/customer/orders/` | 查看所有訂單 | ✅ |
| 訂單詳情 | `/customer/orders/<id>/` | 訂單資訊、付款、申請退款 | ✅ |
| 個人資料 | `/customer/profile/` | 編輯個人資料、上傳頭像 | ✅ |
| 收藏列表 | `/customer/favorites/` | 查看收藏的商品 | ✅ |
| 通知中心 | `/customer/notifications/` | 查看通知、標記已讀 | ✅ |

### 6.2 金流系統頁面

| 頁面 | URL | 功能 | 狀態 |
|------|-----|------|------|
| 付款方式 | `/payment/methods/` | 查看可用付款方式 | ✅ |
| 處理付款 | `/payment/process/<order_id>/` | 選擇付款方式、完成付款 | ✅ |
| 支付詳情 | `/payment/transaction/<id>/` | 查看支付交易詳情 | ✅ |
| 交易記錄 | `/payment/transactions/` | 查看所有交易記錄 | ✅ |
| 申請退款 | `/payment/refund/<order_id>/` | 填寫退款原因、提交申請 | ✅ |
| 退款詳情 | `/payment/refund/detail/<id>/` | 查看退款詳情 | ✅ |
| 退款列表 | `/payment/refunds/` | 查看所有退款記錄 | ✅ |

### 6.3 管理者系統頁面

| 頁面 | URL | 功能 | 狀態 |
|------|-----|------|------|
| 管理後台 | `/administrator/dashboard/` | 統計資料、待處理事項 | ✅ |
| 商品管理 | `/administrator/products/` | 商品列表、搜尋、篩選 | ✅ |
| 新增商品 | `/administrator/products/create/` | 建立新商品 | ✅ |
| 編輯商品 | `/administrator/products/<id>/edit/` | 編輯商品資訊 | ✅ |
| 訂單管理 | `/administrator/orders/` | 訂單列表、搜尋、篩選 | ✅ |
| 訂單詳情 | `/administrator/orders/<id>/` | 訂單詳情、更新狀態 | ✅ |
| 退款管理 | `/administrator/refunds/` | 退款列表、審核退款 | ✅ |
| 使用者管理 | `/administrator/users/` | 使用者列表、搜尋 | ✅ |
| 系統日誌 | `/administrator/logs/` | 系統操作記錄 | ✅ |

---

## 七、API 端點

### 7.1 JSON API (AJAX)

| 端點 | 方法 | 功能 | 回應 |
|------|------|------|------|
| `/customer/products/<id>/favorite/` | POST | 切換收藏狀態 | `{is_favorited: bool}` |
| `/customer/notifications/<id>/read/` | POST | 標記通知已讀 | `{success: bool}` |

---

## 八、資料驗證與錯誤處理

### 8.1 表單驗證
- Django ModelForm 自動驗證
- 自訂驗證規則
- 錯誤訊息顯示

### 8.2 業務邏輯驗證
- 庫存檢查
- 訂單狀態檢查
- 權限檢查
- 資料完整性檢查

### 8.3 錯誤處理
- 404 錯誤頁面
- 403 權限錯誤
- 表單錯誤提示
- 訊息系統 (Django Messages)

---

## 九、效能優化

### 9.1 資料庫優化
- 使用 `select_related()` 減少查詢
- 使用 `prefetch_related()` 優化關聯查詢
- 資料庫索引

### 9.2 分頁
- 所有列表頁面都使用分頁
- 預設每頁 10-20 筆資料

### 9.3 快取策略
- 可擴展至 Redis 快取
- 靜態檔案快取

---

## 十、擴展性設計

### 10.1 模組化設計
- 四個獨立子系統
- 清晰的職責分離
- 易於維護與擴展

### 10.2 可擴展功能
- 第三方支付整合（目前為模擬）
- 多語言支援
- 多貨幣支援
- 促銷活動系統
- 推薦系統

---

## 十一、部署建議

### 11.1 開發環境
- SQLite 資料庫
- Django 開發伺服器
- DEBUG = True

### 11.2 生產環境
- PostgreSQL/MySQL 資料庫
- Gunicorn + Nginx
- DEBUG = False
- 設定 SECRET_KEY
- 設定 ALLOWED_HOSTS
- 使用 HTTPS
- 設定靜態檔案服務
- 設定媒體檔案服務

---

## 十二、測試建議

### 12.1 單元測試
- 模型測試
- 視圖測試
- 表單測試

### 12.2 整合測試
- 購物流程測試
- 支付流程測試
- 退款流程測試

### 12.3 功能測試
- 使用者註冊/登入
- 商品瀏覽與搜尋
- 購物車操作
- 訂單建立與管理
- 支付處理
- 退款申請與處理

---

## 十三、已知限制與未來改進

### 13.1 目前限制
1. 支付功能為模擬實作，需整合第三方支付 API
2. 圖片上傳功能需設定適當的儲存空間
3. 未實作即時通知（WebSocket）
4. 未實作商品庫存預警

### 13.2 未來改進方向
1. 整合真實支付 API（綠界、藍新等）
2. 實作商品庫存管理系統
3. 實作促銷活動系統
4. 實作推薦系統（AI 推薦）
5. 實作即時客服系統
6. 實作多語言支援
7. 實作行動裝置 APP
8. 實作資料分析報表

---

## 十四、維護與支援

### 14.1 系統日誌
- 所有重要操作都記錄在 SystemLog
- 可用於問題追蹤與審計

### 14.2 資料備份
- 建議定期備份資料庫
- 備份媒體檔案

### 14.3 監控建議
- 監控系統效能
- 監控錯誤日誌
- 監控資料庫效能

---

## 十五、聯絡資訊

- **系統名稱**: FOMO 線上購物網站系統 (FOSWS)
- **版本**: 1.0.0
- **開發日期**: 2025年
- **文件版本**: 1.0

---

**文件結束**

