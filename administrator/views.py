"""
管理者系統 (AS) - 視圖
根據 FOMO 系統需求規格書建立
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from database.models import (
    Product, Category, Order, OrderItem, CustomerProfile,
    ProductReview, Notification, Coupon, ProductQuestion
)
from payment.models import PaymentTransaction, Refund
from .models import SystemLog
from datetime import datetime, timedelta


def is_admin(user):
    """檢查是否為管理者"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """管理後台首頁"""
    # 統計資料
    total_orders = Order.objects.count()
    total_revenue = PaymentTransaction.objects.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    today_orders = Order.objects.filter(
        created_at__date=datetime.now().date()
    ).count()
    
    today_revenue = PaymentTransaction.objects.filter(
        status='completed',
        completed_at__date=datetime.now().date()
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    pending_orders = Order.objects.filter(status='pending').count()
    pending_refunds = Refund.objects.filter(status='pending').count()
    pending_questions = ProductQuestion.objects.filter(answer='').count()
    pending_tickets = CustomerServiceTicket.objects.filter(status='open').count()
    
    # 最近訂單
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    # 熱門商品
    popular_products = Product.objects.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:10]
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'pending_orders': pending_orders,
        'pending_refunds': pending_refunds,
        'pending_questions': pending_questions,
        'pending_tickets': pending_tickets,
        'recent_orders': recent_orders,
        'popular_products': popular_products,
    }
    return render(request, 'administrator/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def product_management(request):
    """商品管理"""
    products = Product.objects.all().order_by('-created_at')
    
    search_query = request.GET.get('search')
    status_filter = request.GET.get('status')
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if status_filter:
        products = products.filter(status=status_filter)
    
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'administrator/product_management.html', context)


@login_required
@user_passes_test(is_admin)
def product_create(request):
    """新增商品"""
    from database.forms import ProductForm
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            SystemLog.objects.create(
                user=request.user,
                action='create',
                model_name='Product',
                object_id=str(product.id),
                description=f'建立商品: {product.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, '商品已建立')
            return redirect('administrator:product_management')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
    }
    return render(request, 'administrator/product_form.html', context)


@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    """編輯商品"""
    product = get_object_or_404(Product, pk=pk)
    from database.forms import ProductForm
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            SystemLog.objects.create(
                user=request.user,
                action='update',
                model_name='Product',
                object_id=str(product.id),
                description=f'更新商品: {product.name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, '商品已更新')
            return redirect('administrator:product_management')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'administrator/product_form.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def product_delete(request, pk):
    """刪除商品"""
    product = get_object_or_404(Product, pk=pk)
    product_name = product.name
    product.delete()
    
    SystemLog.objects.create(
        user=request.user,
        action='delete',
        model_name='Product',
        object_id=str(pk),
        description=f'刪除商品: {product_name}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(request, '商品已刪除')
    return redirect('administrator:product_management')


@login_required
@user_passes_test(is_admin)
def order_management(request):
    """訂單管理"""
    orders = Order.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'administrator/order_management.html', context)


@login_required
@user_passes_test(is_admin)
def order_detail_admin(request, order_id):
    """訂單詳情（管理者）"""
    order = get_object_or_404(Order, pk=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            order.save()
            
            SystemLog.objects.create(
                user=request.user,
                action='update',
                model_name='Order',
                object_id=str(order.id),
                description=f'訂單狀態從 {old_status} 變更為 {new_status}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            # 建立通知
            Notification.objects.create(
                user=order.user,
                type='order',
                title='訂單狀態更新',
                message=f'您的訂單 {order.order_number} 狀態已更新為 {order.get_status_display()}'
            )
            
            messages.success(request, '訂單狀態已更新')
    
    context = {
        'order': order,
    }
    return render(request, 'administrator/order_detail.html', context)


@login_required
@user_passes_test(is_admin)
def refund_management(request):
    """退款管理"""
    refunds = Refund.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter:
        refunds = refunds.filter(status=status_filter)
    
    paginator = Paginator(refunds, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'refunds': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'administrator/refund_management.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def process_refund(request, refund_id):
    """處理退款"""
    refund = get_object_or_404(Refund, pk=refund_id)
    action = request.POST.get('action')
    
    if action == 'approve':
        refund.status = 'completed'
        refund.completed_at = datetime.now()
        refund.save()
        
        # 更新訂單狀態
        refund.order.status = 'refunded'
        refund.order.save()
        
        SystemLog.objects.create(
            user=request.user,
            action='update',
            model_name='Refund',
            object_id=str(refund.id),
            description=f'核准退款: {refund.refund_id}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # 建立通知
        Notification.objects.create(
            user=refund.order.user,
            type='payment',
            title='退款已完成',
            message=f'您的退款申請 {refund.refund_id} 已完成，金額 {refund.amount} 元'
        )
        
        messages.success(request, '退款已核准')
    elif action == 'reject':
        refund.status = 'rejected'
        refund.save()
        
        SystemLog.objects.create(
            user=request.user,
            action='update',
            model_name='Refund',
            object_id=str(refund.id),
            description=f'拒絕退款: {refund.refund_id}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # 建立通知
        Notification.objects.create(
            user=refund.order.user,
            type='payment',
            title='退款申請已拒絕',
            message=f'您的退款申請 {refund.refund_id} 已被拒絕'
        )
        
        messages.success(request, '退款已拒絕')
    
    return redirect('administrator:refund_management')


@login_required
@user_passes_test(is_admin)
def user_management(request):
    """使用者管理"""
    users = CustomerProfile.objects.all().select_related('user').order_by('-created_at')
    
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(user__username__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search_query': search_query,
    }
    return render(request, 'administrator/user_management.html', context)


@login_required
@user_passes_test(is_admin)
def system_logs(request):
    """系統日誌"""
    logs = SystemLog.objects.all().order_by('-created_at')
    
    action_filter = request.GET.get('action')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'logs': page_obj,
        'action_filter': action_filter,
    }
    return render(request, 'administrator/system_logs.html', context)


@login_required
@user_passes_test(is_admin)
def question_management(request):
    """問答管理"""
    questions = ProductQuestion.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter == 'answered':
        questions = questions.exclude(answer='')
    elif status_filter == 'unanswered':
        questions = questions.filter(answer='')
    
    paginator = Paginator(questions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'questions': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'administrator/question_management.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def answer_question(request, question_id):
    """回答問題"""
    question = get_object_or_404(ProductQuestion, pk=question_id)
    answer_text = request.POST.get('answer', '').strip()
    
    if not answer_text:
        messages.error(request, '請輸入回答')
        return redirect('administrator:question_management')
    
    question.answer = answer_text
    question.answered_by = request.user
    question.answered_at = datetime.now()
    question.save()
    
    SystemLog.objects.create(
        user=request.user,
        action='update',
        model_name='ProductQuestion',
        object_id=str(question.id),
        description=f'回答問題: {question.product.name}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    # 建立通知
    Notification.objects.create(
        user=question.user,
        type='system',
        title='問題已回覆',
        message=f'您對商品 {question.product.name} 的提問已獲得回覆'
    )
    
    messages.success(request, '問題已回覆')
    return redirect('administrator:question_management')


@login_required
@user_passes_test(is_admin)
def ticket_management(request):
    """客服工單管理"""
    tickets = CustomerServiceTicket.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    
    paginator = Paginator(tickets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tickets': page_obj,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'administrator/ticket_management.html', context)


@login_required
@user_passes_test(is_admin)
def ticket_detail_admin(request, ticket_id):
    """客服工單詳情（管理者）"""
    ticket = get_object_or_404(CustomerServiceTicket, pk=ticket_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        message_text = request.POST.get('message', '').strip()
        
        if action == 'reply' and message_text:
            CustomerServiceMessage.objects.create(
                ticket=ticket,
                user=request.user,
                message=message_text,
                is_from_staff=True
            )
            if ticket.status == 'open':
                ticket.status = 'in_progress'
                ticket.assigned_to = request.user
            ticket.updated_at = datetime.now()
            ticket.save()
            messages.success(request, '回覆已發送')
        elif action == 'assign':
            ticket.assigned_to = request.user
            ticket.status = 'in_progress'
            ticket.save()
            messages.success(request, '工單已指派給您')
        elif action == 'resolve':
            ticket.status = 'resolved'
            ticket.resolved_at = datetime.now()
            ticket.save()
            messages.success(request, '工單已標記為已解決')
        elif action == 'close':
            ticket.status = 'closed'
            ticket.save()
            messages.success(request, '工單已關閉')
        
        SystemLog.objects.create(
            user=request.user,
            action='update',
            model_name='CustomerServiceTicket',
            object_id=str(ticket.id),
            description=f'更新工單狀態: {ticket.status}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return redirect('administrator:ticket_detail', ticket_id=ticket_id)
    
    messages_list = ticket.messages.all()
    context = {
        'ticket': ticket,
        'messages': messages_list,
    }
    return render(request, 'administrator/ticket_detail.html', context)


@login_required
@user_passes_test(is_admin)
def faq_management(request):
    """FAQ 管理"""
    faqs = FAQ.objects.all().order_by('order', '-created_at')
    
    category_filter = request.GET.get('category')
    if category_filter:
        faqs = faqs.filter(category=category_filter)
    
    paginator = Paginator(faqs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'faqs': page_obj,
        'category_filter': category_filter,
    }
    return render(request, 'administrator/faq_management.html', context)


@login_required
@user_passes_test(is_admin)
def faq_create(request):
    """新增 FAQ"""
    if request.method == 'POST':
        category = request.POST.get('category')
        question = request.POST.get('question', '').strip()
        answer = request.POST.get('answer', '').strip()
        order = int(request.POST.get('order', 0))
        is_active = request.POST.get('is_active') == 'on'
        
        if not question or not answer:
            messages.error(request, '請填寫問題和回答')
            return render(request, 'administrator/faq_form.html')
        
        faq = FAQ.objects.create(
            category=category,
            question=question,
            answer=answer,
            order=order,
            is_active=is_active
        )
        
        SystemLog.objects.create(
            user=request.user,
            action='create',
            model_name='FAQ',
            object_id=str(faq.id),
            description=f'建立 FAQ: {question}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'FAQ 已建立')
        return redirect('administrator:faq_management')
    
    return render(request, 'administrator/faq_form.html')


@login_required
@user_passes_test(is_admin)
def faq_edit(request, faq_id):
    """編輯 FAQ"""
    faq = get_object_or_404(FAQ, pk=faq_id)
    
    if request.method == 'POST':
        faq.category = request.POST.get('category')
        faq.question = request.POST.get('question', '').strip()
        faq.answer = request.POST.get('answer', '').strip()
        faq.order = int(request.POST.get('order', 0))
        faq.is_active = request.POST.get('is_active') == 'on'
        faq.save()
        
        SystemLog.objects.create(
            user=request.user,
            action='update',
            model_name='FAQ',
            object_id=str(faq.id),
            description=f'更新 FAQ: {faq.question}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'FAQ 已更新')
        return redirect('administrator:faq_management')
    
    context = {
        'faq': faq,
    }
    return render(request, 'administrator/faq_form.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def faq_delete(request, faq_id):
    """刪除 FAQ"""
    faq = get_object_or_404(FAQ, pk=faq_id)
    faq.delete()
    
    SystemLog.objects.create(
        user=request.user,
        action='delete',
        model_name='FAQ',
        object_id=str(faq_id),
        description=f'刪除 FAQ: {faq.question}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(request, 'FAQ 已刪除')
    return redirect('administrator:faq_management')
