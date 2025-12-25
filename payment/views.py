"""
金流系統 (PS) - 視圖
根據 FOMO 系統需求規格書建立
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from database.models import Order, Notification
from .models import PaymentMethod, PaymentTransaction, Refund, CustomerServiceTicket, CustomerServiceMessage, FAQ, PaymentAccount
import uuid
from datetime import datetime


@login_required
def payment_methods(request):
    """付款方式列表"""
    methods = PaymentMethod.objects.filter(is_active=True)
    return render(request, 'payment/methods.html', {'methods': methods})


@login_required
def process_payment(request, order_id):
    """處理支付"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    if order.status != 'pending':
        messages.error(request, '此訂單無法付款')
        return redirect('customer:order_detail', order_id=order_id)
    
    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        payment_method = get_object_or_404(PaymentMethod, pk=payment_method_id, is_active=True)
        
        # 建立交易記錄
        transaction_id = f"TXN{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        transaction = PaymentTransaction.objects.create(
            order=order,
            user=request.user,
            payment_method=payment_method,
            transaction_id=transaction_id,
            amount=order.total_amount,
            status='processing'
        )
        
        # 模擬支付處理（實際應整合第三方支付API）
        # 這裡簡化處理，直接標記為完成
        transaction.status = 'completed'
        transaction.completed_at = datetime.now()
        transaction.save()
        
        # 更新訂單狀態
        order.status = 'paid'
        order.save()
        
        # 建立通知
        from database.models import Notification
        Notification.objects.create(
            user=request.user,
            type='payment',
            title='付款成功',
            message=f'您的訂單 {order.order_number} 付款成功，金額 {order.total_amount} 元'
        )
        
        messages.success(request, '付款成功')
        return redirect('payment:payment_detail', transaction_id=transaction.id)
    
    methods = PaymentMethod.objects.filter(is_active=True)
    context = {
        'order': order,
        'methods': methods,
    }
    return render(request, 'payment/process_payment.html', context)


@login_required
def payment_detail(request, transaction_id):
    """支付詳情"""
    transaction = get_object_or_404(PaymentTransaction, pk=transaction_id, user=request.user)
    context = {
        'transaction': transaction,
    }
    return render(request, 'payment/payment_detail.html', context)


@login_required
def transaction_history(request):
    """交易記錄"""
    transactions = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')
    
    from django.core.paginator import Paginator
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'transactions': page_obj,
    }
    return render(request, 'payment/transaction_history.html', context)


@login_required
def request_refund(request, order_id):
    """申請退款"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    if order.status not in ['paid', 'processing', 'shipped']:
        messages.error(request, '此訂單無法申請退款')
        return redirect('customer:order_detail', order_id=order_id)
    
    # 檢查是否已有退款申請
    existing_refund = Refund.objects.filter(order=order, status__in=['pending', 'processing']).first()
    if existing_refund:
        messages.error(request, '您已有待處理的退款申請')
        return redirect('customer:order_detail', order_id=order_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        if not reason:
            messages.error(request, '請填寫退款原因')
            return render(request, 'payment/request_refund.html', {'order': order})
        
        # 取得支付交易
        payment_transaction = PaymentTransaction.objects.filter(
            order=order,
            status='completed'
        ).first()
        
        if not payment_transaction:
            messages.error(request, '找不到支付記錄')
            return redirect('customer:order_detail', order_id=order_id)
        
        # 建立退款記錄
        refund_id = f"REF{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        refund = Refund.objects.create(
            payment_transaction=payment_transaction,
            order=order,
            refund_id=refund_id,
            amount=order.total_amount,
            reason=reason,
            status='pending'
        )
        
        # 建立通知
        from database.models import Notification
        Notification.objects.create(
            user=request.user,
            type='payment',
            title='退款申請已提交',
            message=f'您的退款申請 {refund_id} 已提交，我們將盡快處理'
        )
        
        messages.success(request, '退款申請已提交')
        return redirect('payment:refund_detail', refund_id=refund.id)
    
    context = {
        'order': order,
    }
    return render(request, 'payment/request_refund.html', context)


@login_required
def refund_detail(request, refund_id):
    """退款詳情"""
    refund = get_object_or_404(Refund, pk=refund_id, order__user=request.user)
    context = {
        'refund': refund,
    }
    return render(request, 'payment/refund_detail.html', context)


@login_required
def refund_list(request):
    """退款列表"""
    refunds = Refund.objects.filter(order__user=request.user).order_by('-created_at')
    
    from django.core.paginator import Paginator
    paginator = Paginator(refunds, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'refunds': page_obj,
    }
    return render(request, 'payment/refund_list.html', context)


@login_required
def faq_list(request):
    """常見問題列表"""
    faqs = FAQ.objects.filter(is_active=True).order_by('order', '-created_at')
    
    category_filter = request.GET.get('category')
    if category_filter:
        faqs = faqs.filter(category=category_filter)
    
    context = {
        'faqs': faqs,
        'category_filter': category_filter,
    }
    return render(request, 'payment/faq_list.html', context)


@login_required
def create_ticket(request):
    """建立客服工單"""
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'medium')
        order_id = request.POST.get('order_id', '')
        
        if not subject or not description:
            messages.error(request, '請填寫主旨和問題描述')
            return render(request, 'payment/create_ticket.html', {
                'orders': Order.objects.filter(user=request.user) if request.user.is_authenticated else []
            })
        
        ticket = CustomerServiceTicket.objects.create(
            user=request.user,
            subject=subject,
            description=description,
            priority=priority,
            related_order_id=order_id if order_id else None,
            status='open'
        )
        
        Notification.objects.create(
            user=request.user,
            type='system',
            title='客服工單已建立',
            message=f'您的客服工單 #{ticket.id} 已建立，我們將盡快處理'
        )
        
        messages.success(request, f'客服工單 #{ticket.id} 已建立')
        return redirect('payment:ticket_detail', ticket_id=ticket.id)
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]
    context = {
        'orders': orders,
    }
    return render(request, 'payment/create_ticket.html', context)


@login_required
def ticket_list(request):
    """客服工單列表"""
    tickets = CustomerServiceTicket.objects.filter(user=request.user).order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    from django.core.paginator import Paginator
    paginator = Paginator(tickets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tickets': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'payment/ticket_list.html', context)


@login_required
def ticket_detail(request, ticket_id):
    """客服工單詳情"""
    ticket = get_object_or_404(CustomerServiceTicket, pk=ticket_id, user=request.user)
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            CustomerServiceMessage.objects.create(
                ticket=ticket,
                user=request.user,
                message=message_text,
                is_from_staff=False
            )
            ticket.updated_at = datetime.now()
            ticket.save()
            messages.success(request, '訊息已發送')
            return redirect('payment:ticket_detail', ticket_id=ticket_id)
    
    messages_list = ticket.messages.all()
    context = {
        'ticket': ticket,
        'messages': messages_list,
    }
    return render(request, 'payment/ticket_detail.html', context)


@login_required
def payment_accounts(request):
    """付款帳號管理"""
    accounts = PaymentAccount.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    context = {
        'accounts': accounts,
    }
    return render(request, 'payment/payment_accounts.html', context)


@login_required
def add_payment_account(request):
    """新增付款帳號"""
    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        account_name = request.POST.get('account_name', '').strip()
        account_info = {}
        
        payment_method = get_object_or_404(PaymentMethod, pk=payment_method_id, is_active=True)
        
        # 根據付款方式收集不同的資訊
        if payment_method.code == 'credit_card':
            account_info = {
                'card_number': request.POST.get('card_number', ''),
                'card_holder': request.POST.get('card_holder', ''),
                'expiry_date': request.POST.get('expiry_date', ''),
            }
        elif payment_method.code == 'bank_transfer':
            account_info = {
                'bank_name': request.POST.get('bank_name', ''),
                'account_number': request.POST.get('account_number', ''),
                'account_holder': request.POST.get('account_holder', ''),
            }
        
        is_default = request.POST.get('is_default') == 'on'
        
        # 如果設為預設，取消其他預設
        if is_default:
            PaymentAccount.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        PaymentAccount.objects.create(
            user=request.user,
            payment_method=payment_method,
            account_name=account_name,
            account_info=account_info,
            is_default=is_default
        )
        
        messages.success(request, '付款帳號已新增')
        return redirect('payment:payment_accounts')
    
    methods = PaymentMethod.objects.filter(is_active=True)
    context = {
        'methods': methods,
    }
    return render(request, 'payment/add_payment_account.html', context)


@login_required
@require_POST
def set_default_account(request, account_id):
    """設定預設帳號"""
    account = get_object_or_404(PaymentAccount, pk=account_id, user=request.user)
    
    # 取消其他預設
    PaymentAccount.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # 設定為預設
    account.is_default = True
    account.save()
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def delete_payment_account(request, account_id):
    """刪除付款帳號"""
    account = get_object_or_404(PaymentAccount, pk=account_id, user=request.user)
    account.delete()
    messages.success(request, '付款帳號已刪除')
    return redirect('payment:payment_accounts')
