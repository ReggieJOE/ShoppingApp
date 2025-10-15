from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .forms import UserRegisterForm, CheckoutForm
from django.contrib.auth import logout as auth_logout
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(stock__gt=0)[:8]
    return render(request, 'home.html', {
        'categories': categories,
        'featured_products': featured_products})


def product_list(request, category_id=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(stock__gt=0)

    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=category)
    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
        'category': category})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account successfully created.')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f'{product.name} added to cart!')
    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart!')
    return redirect('view_cart')


@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('view_cart')


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    if not cart.items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('view_cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.total_amount = cart.get_total_price()
                order.save()

                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                    # Update stock
                    cart_item.product.stock -= cart_item.quantity
                    cart_item.product.save()

                # Clear cart
                cart.items.all().delete()

                messages.success(request, 'Order placed successfully!')
                return redirect('order_success', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {
        'cart': cart,
        'form': form
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})


def custom_logout(request):
    auth_logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('home')


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    # Statistics
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_customers = User.objects.filter(is_staff=False).count()

    # Recent orders
    recent_orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')[:10]

    # Sales data for chart (last 7 days)
    today = timezone.now().date()
    last_week = today - timedelta(days=7)

    daily_sales = Order.objects.filter(
        created_atdategte=last_week
    ).values('created_at__date').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('created_at__date')

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'daily_sales': list(daily_sales),
    }

    return render(request, 'admin_dashboard.html', context)


@login_required
def order_history(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')

    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'order_history.html', context)


@login_required
def customer_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    customers = User.objects.filter(is_staff=False).annotate(
        total_orders=Count('order'),
        total_spent=Sum('order__total_amount')
    ).order_by('-date_joined')

    context = {
        'customers': customers,
    }
    return render(request, 'customer_list.html', context)
