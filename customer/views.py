"""
顧客系統 (CS) - 視圖
根據 FOMO 系統需求規格書建立
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from database.models import (
    Product, Category, ShoppingCart, Order, OrderItem,
    ProductReview, Favorite, CustomerProfile, Notification, Coupon, ProductQuestion,
    ProductTracking, ProductPriceHistory
)
from payment.models import PaymentTransaction
import uuid
from datetime import datetime


def product_list(request):
    """商品列表"""
    products = Product.objects.filter(status='active')
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    sort_by = request.GET.get('sort', 'newest')
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        products = products.order_by('-created_at')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'current_category': category_id,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'customer/product_list.html', context)


def product_detail(request, pk):
    """商品詳情"""
    product = get_object_or_404(Product, pk=pk)
    product.view_count += 1
    product.save()
    
    reviews = ProductReview.objects.filter(product=product).order_by('-created_at')[:10]
    questions = ProductQuestion.objects.filter(product=product, is_public=True).order_by('-created_at')[:10]
    
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, product=product).exists()
    
    related_products = Product.objects.filter(
        category=product.category,
        status='active'
    ).exclude(pk=pk)[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'questions': questions,
        'is_favorited': is_favorited,
        'related_products': related_products,
    }
    return render(request, 'customer/product_detail.html', context)


@login_required
def add_to_cart(request, product_id):
    """加入購物車"""
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if product.stock < quantity:
        messages.error(request, '庫存不足')
        return redirect('customer:product_detail', pk=product_id)
    
    cart_item, created = ShoppingCart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        if cart_item.quantity > product.stock:
            cart_item.quantity = product.stock
        cart_item.save()
    
    messages.success(request, f'已將 {product.name} 加入購物車')
    return redirect('customer:cart')


@login_required
def cart(request):
    """購物車"""
    cart_items = ShoppingCart.objects.filter(user=request.user)
    total = sum(item.subtotal for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'customer/cart.html', context)


@login_required
@require_POST
def update_cart(request, cart_id):
    """更新購物車項目"""
    cart_item = get_object_or_404(ShoppingCart, pk=cart_id, user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, '已從購物車移除')
    else:
        if quantity > cart_item.product.stock:
            messages.error(request, '庫存不足')
            return redirect('customer:cart')
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, '購物車已更新')
    
    return redirect('customer:cart')


@login_required
@require_POST
def remove_from_cart(request, cart_id):
    """從購物車移除"""
    cart_item = get_object_or_404(ShoppingCart, pk=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, '已從購物車移除')
    return redirect('customer:cart')


@login_required
def checkout(request):
    """結帳"""
    cart_items = ShoppingCart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, '購物車是空的')
        return redirect('customer:cart')
    
    # 檢查庫存
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request, f'{item.product.name} 庫存不足')
            return redirect('customer:cart')
    
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        shipping_phone = request.POST.get('shipping_phone')
        coupon_code = request.POST.get('coupon_code', '')
        notes = request.POST.get('notes', '')
        
        if not shipping_address or not shipping_phone:
            messages.error(request, '請填寫配送資訊')
            return render(request, 'customer/checkout.html', {
                'cart_items': cart_items,
                'profile': profile,
            })
        
        # 計算總金額
        total = sum(item.subtotal for item in cart_items)
        discount = 0
        
        # 檢查優惠券
        if coupon_code:
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code,
                    is_active=True,
                    valid_from__lte=datetime.now(),
                    valid_until__gte=datetime.now()
                )
                if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
                    messages.error(request, '優惠券已達使用上限')
                elif total < coupon.min_purchase:
                    messages.error(request, f'未達最低消費 {coupon.min_purchase} 元')
                else:
                    if coupon.discount_type == 'percentage':
                        discount = total * (coupon.discount_value / 100)
                        if coupon.max_discount:
                            discount = min(discount, coupon.max_discount)
                    else:
                        discount = coupon.discount_value
                    total -= discount
            except Coupon.DoesNotExist:
                messages.error(request, '無效的優惠券')
        
        # 建立訂單
        order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_amount=total,
            shipping_address=shipping_address,
            shipping_phone=shipping_phone,
            notes=notes,
            status='pending'
        )
        
        # 建立訂單項目
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                subtotal=item.subtotal
            )
            # 減少庫存
            item.product.stock -= item.quantity
            item.product.save()
        
        # 清空購物車
        cart_items.delete()
        
        # 建立通知
        Notification.objects.create(
            user=request.user,
            type='order',
            title='訂單已建立',
            message=f'您的訂單 {order_number} 已建立，請完成付款'
        )
        
        messages.success(request, '訂單已建立')
        return redirect('customer:order_detail', order_id=order.id)
    
    total = sum(item.subtotal for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total': total,
        'profile': profile,
    }
    return render(request, 'customer/checkout.html', context)


@login_required
def order_list(request):
    """訂單列表"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
    }
    return render(request, 'customer/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """訂單詳情"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'customer/order_detail.html', context)


@login_required
def profile(request):
    """個人資料"""
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        if request.POST.get('birth_date'):
            profile.birth_date = request.POST.get('birth_date')
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, '資料已更新')
        return redirect('customer:profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'customer/profile.html', context)


@login_required
@require_POST
def add_review(request, product_id):
    """新增評價"""
    product = get_object_or_404(Product, pk=product_id)
    rating = int(request.POST.get('rating'))
    comment = request.POST.get('comment', '')
    
    # 檢查是否已購買
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status__in=['paid', 'processing', 'shipped', 'delivered']
    ).exists()
    
    if not has_purchased:
        messages.error(request, '只有購買過的顧客才能評價')
        return redirect('customer:product_detail', pk=product_id)
    
    # 檢查是否已評價
    review, created = ProductReview.objects.get_or_create(
        product=product,
        user=request.user,
        defaults={'rating': rating, 'comment': comment}
    )
    
    if not created:
        review.rating = rating
        review.comment = comment
        review.save()
        messages.success(request, '評價已更新')
    else:
        messages.success(request, '評價已新增')
    
    return redirect('customer:product_detail', pk=product_id)


@login_required
@require_POST
def toggle_favorite(request, product_id):
    """切換收藏狀態"""
    product = get_object_or_404(Product, pk=product_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if not created:
        favorite.delete()
        return JsonResponse({'is_favorited': False})
    
    return JsonResponse({'is_favorited': True})


@login_required
def favorite_list(request):
    """收藏列表"""
    favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(favorites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'favorites': page_obj,
    }
    return render(request, 'customer/favorite_list.html', context)


@login_required
def notification_list(request):
    """通知列表"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': unread_count,
    }
    return render(request, 'customer/notification_list.html', context)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """標記通知為已讀"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


@login_required
@require_POST
def ask_question(request, product_id):
    """提問功能"""
    product = get_object_or_404(Product, pk=product_id)
    question_text = request.POST.get('question', '').strip()
    
    if not question_text:
        messages.error(request, '請輸入問題')
        return redirect('customer:product_detail', pk=product_id)
    
    ProductQuestion.objects.create(
        product=product,
        user=request.user,
        question=question_text,
        is_public=True
    )
    
    messages.success(request, '問題已提交，我們將盡快回覆')
    return redirect('customer:product_detail', pk=product_id)


@login_required
@require_POST
def track_product(request, product_id):
    """追蹤商品"""
    product = get_object_or_404(Product, pk=product_id)
    track_price = request.POST.get('track_price') == 'on'
    track_stock = request.POST.get('track_stock') == 'on'
    track_status = request.POST.get('track_status') == 'on'
    
    tracking, created = ProductTracking.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={
            'track_price': track_price,
            'track_stock': track_stock,
            'track_status': track_status
        }
    )
    
    if not created:
        tracking.track_price = track_price
        tracking.track_stock = track_stock
        tracking.track_status = track_status
        tracking.save()
    
    return JsonResponse({'success': True, 'is_tracked': True})


@login_required
@require_POST
def untrack_product(request, product_id):
    """取消追蹤商品"""
    product = get_object_or_404(Product, pk=product_id)
    ProductTracking.objects.filter(user=request.user, product=product).delete()
    return JsonResponse({'success': True, 'is_tracked': False})


@login_required
def tracked_products(request):
    """追蹤商品列表"""
    trackings = ProductTracking.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(trackings, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'trackings': page_obj,
    }
    return render(request, 'customer/tracked_products.html', context)
