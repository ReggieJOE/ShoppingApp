from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Product, Category, Cart, CartItem, Order, OrderItem, User
from .forms import UserRegisterForm, CheckoutForm, ProductForm
from django.contrib.auth import logout as auth_logout
from django.db.models import Sum, Count, Max, Q
from datetime import date
from functools import wraps


# ========== DECORATORS ==========
def staff_required(view_func):
    """Decorator to ensure user is staff member"""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('home')
        return view_func(request, *args, **kwargs)

    return wrapper


# ========== MAIN SITE VIEWS ==========
def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(stock__gt=0).distinct()[:8]
    return render(request, 'home.html', {
        'categories': categories,
        'featured_products': featured_products,
    })


def product_list(request, category_id=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(stock__gt=0)

    if category_id:
        category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=category)

    products = products.distinct()
    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
        'category': category
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})


def register(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in!')
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegisterForm()

    return render(request, 'register_fixed.html', {'form': form})


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items_count = cart.items.count()
    return render(request, 'cart.html', {
        'cart': cart,
        'cart_items_count': cart_items_count
    })


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
            try:
                with transaction.atomic():
                    shipping_address = form.cleaned_data['shipping_address']
                    payment_method = form.cleaned_data['payment_method']

                    order = Order.objects.create(
                        user=request.user,
                        total_amount=cart.get_total_price(),
                        shipping_address=shipping_address,
                        payment_method=payment_method,
                        status='pending'
                    )

                    for cart_item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            price=cart_item.product.price
                        )
                        cart_item.product.stock -= cart_item.quantity
                        cart_item.product.save()

                    cart.items.all().delete()
                    messages.success(request, 'Order placed successfully!')
                    return redirect('order_success', order_id=order.id)
            except Exception as e:
                messages.error(request, f'An error occurred while processing your order: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
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


# ========== ADMIN VIEWS ==========
@login_required
@staff_required
def admin_dashboard(request):
    """Admin dashboard view - Overview with quick stats"""
    try:
        # Basic statistics
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        total_customers = User.objects.filter(is_staff=False).count()
        total_products = Product.objects.count()

        # Recent data
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        recent_users = User.objects.filter(is_staff=False).order_by('-date_joined')[:5]

        # Top customers with order stats
        top_customers = User.objects.filter(
            order__isnull=False
        ).annotate(
            total_orders=Count('order'),
            total_spent=Sum('order__total_amount')
        ).order_by('-total_spent')[:5]

        # Additional stats
        categories = Category.objects.all()
        active_carts = Cart.objects.count()
        today_orders = Order.objects.filter(created_at__date=date.today()).count()
        low_stock_products = Product.objects.filter(stock__lt=10)[:5]
        context = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_customers': total_customers,
            'total_products': total_products,
            'recent_orders': recent_orders,
            'recent_users': recent_users,
            'top_customers': top_customers,
            'categories': categories,
            'active_carts': active_carts,
            'today_orders': today_orders,
            'low_stock_products': low_stock_products,
        }
        return render(request, 'admin/admin_dashboard.html', context)

    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
    return redirect('home')



@login_required
@staff_required
def admin_products(request):
    """Product management view with filtering and search"""
    products = Product.objects.select_related('category').all()
    categories = Category.objects.all()

    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category_id=category_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'products': products,
        'categories': categories,
        'total_products': products.count(),
        'low_stock_products': products.filter(stock__lt=10).count(),
    }

    return render(request, 'admin/admin_products.html', context)


@login_required
@staff_required
def admin_product_edit(request, product_id=None):
    """Handle both add and edit products"""
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        title = f"Edit Product: {product.name}"
    else:
        product = None
        title = "Add New Product"

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            saved_product = form.save()
            action = "updated" if product_id else "created"
            messages.success(request, f'Product "{saved_product.name}" {action} successfully!')
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)
        context = {
            'product': product,
            'form': form,
            'title': title,
        }

        return render(request, 'admin/product_edit.html', context)


@login_required
@staff_required
def admin_product_delete(request, product_id):
    """Delete product"""
    product = get_object_or_404(Product, id=product_id)
    product_name = product.name
    product.delete()
    messages.success(request, f'Product "{product_name}" deleted successfully.')
    return redirect('admin_products')


@login_required
@staff_required
def customer_list(request):
    """View all customers with order statistics"""

    customers = User.objects.filter(is_staff=False).annotate(
        total_orders=Count('order'),
        total_spent=Sum('order__total_amount'),
        last_order_date=Max('order__created_at')
    ).order_by('-date_joined')

    context = {
        'customers': customers,
    }
    return render(request, 'admin/customer_list.html', context)


@login_required
@staff_required
def user_order_history(request, user_id):
    """View detailed order history for a specific user"""
    user_profile = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=user_profile).select_related('user').prefetch_related(
        'items__product').order_by('-created_at')

    # Calculate user statistics
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    avg_order_value = total_spent / total_orders if total_orders > 0 else 0

    context = {
        'user_profile': user_profile,
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'avg_order_value': avg_order_value,
    }
    return render(request, 'admin/user_order_history.html', context)


@login_required
@staff_required
def order_history(request):
    """View all orders with filtering"""
    orders = Order.objects.select_related('user').prefetch_related('items__product').order_by('-created_at')

    # Status filter
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Calculate statistics
    total_orders = orders.count()
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'status_choices': Order.STATUS_CHOICES,
    }

    return render(request, 'order_history.html', context)


@login_required
@staff_required
def admin_categories(request):
    """Category management view"""
    categories = Category.objects.all()

    if request.method == 'POST':
        # Handle category creation
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            Category.objects.create(name=name, description=description)
            messages.success(request, f'Category "{name}" created successfully!')
            return redirect('admin_categories')

    context = {
        'categories': categories,
    }
    return render(request, 'admin/admin_categories.html', context)


@login_required
@staff_required
def admin_category_delete(request, category_id):
    """Delete category"""
    category = get_object_or_404(Category, id=category_id)
    category_name = category.name
    category.delete()
    messages.success(request, f'Category "{category_name}" deleted successfully.')
    return redirect('admin_categories')


@login_required
@staff_required
def update_order_status(request, order_id):
    """Update order status"""
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.get_status_display()
            order.status = new_status
            order.save()
            messages.success(request,
                             f'Order #{order.id} status updated from {old_status} to {order.get_status_display()}')
        else:
            messages.error(request, 'Invalid status selected.')

    return redirect('order_history')