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
import logging


def home(request):
    categories = Category.objects.all()

    # Get featured products without duplicates
    featured_products = Product.objects.filter(stock__gt=0).distinct()[:8]

    # Debug info
    print(f"DEBUG: Found {featured_products.count()} featured products")
    for product in featured_products:
        print(f"DEBUG: Product: {product.name}, ID: {product.id}")

    return render(request, 'home.html', {
        'categories': categories,
        'featured_products': featured_products,
    })


def product_list(request, category_id=None):
    category = None
    categories = Category.objects.all()

    # Start with all products that have stock
    products = Product.objects.filter(stock__gt=0)

    print(f"DEBUG: Initial products count: {products.count()}")

    if category_id:
        category = get_object_or_404(Category, id=category_id)
        # Filter by category
        products = products.filter(category=category)
        print(f"DEBUG: After category filter: {products.count()}")

    # Remove any potential duplicates by using distinct on ID
    products = products.distinct()

    print(f"DEBUG: Final products count: {products.count()}")

    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
        'category': category
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})


logger = logging.getLogger(__name__)


def register(request):
    print("DEBUG: Register view accessed")
    logger.info("Register view accessed - Method: %s", request.method)

    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in!')
        return redirect('home')

    if request.method == 'POST':
        print("DEBUG: POST request to register")
        logger.info("POST request to register")
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            print("DEBUG: Form is valid, creating user")
            logger.info("Form is valid, creating user")
            try:
                user = form.save()
                print(f"DEBUG: User created: {user.username}")
                logger.info("User created successfully: %s", user.username)
                login(request, user)
                messages.success(request, f'Account created successfully! Welcome, {user.username}!')
                return redirect('home')
            except Exception as e:
                print(f"DEBUG: Error creating user: {str(e)}")
                logger.error("Error creating user: %s", str(e))
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            print(f"DEBUG: Form errors: {form.errors}")
            logger.warning("Form errors: %s", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegisterForm()
        print("DEBUG: GET request - showing registration form")
        logger.info("GET request - showing registration form")

    # Use the fixed template
    return render(request, 'register_fixed.html', {'form': form})
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

    print(f"DEBUG: Checkout started for user {request.user.username}")

    if not cart.items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('view_cart')

    if request.method == 'POST':
        print("DEBUG: POST request received")
        form = CheckoutForm(request.POST)
        if form.is_valid():
            print("DEBUG: Form is valid")
            try:
                with transaction.atomic():
                    # Get form data
                    shipping_address = form.cleaned_data['shipping_address']
                    payment_method = form.cleaned_data['payment_method']

                    print(f"DEBUG: Creating order with shipping: {shipping_address}, payment: {payment_method}")

                    # Create order
                    order = Order.objects.create(
                        user=request.user,
                        total_amount=cart.get_total_price(),
                        shipping_address=shipping_address,
                        payment_method=payment_method,
                        status='pending'
                    )

                    print(f"DEBUG: Order created with ID {order.id}")

                    # Create order items
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
                        print(f"DEBUG: Added {cart_item.product.name} to order")

                    # Clear cart
                    cart_items_count = cart.items.count()
                    cart.items.all().delete()
                    print(f"DEBUG: Cleared {cart_items_count} items from cart")

                    messages.success(request, 'Order placed successfully!')
                    print(f"DEBUG: Redirecting to order_success with order_id {order.id}")
                    return redirect('order_success', order_id=order.id)

            except Exception as e:
                print(f"DEBUG: Exception during checkout: {str(e)}")
                import traceback
                print(f"DEBUG: Traceback: {traceback.format_exc()}")
                messages.error(request, f'An error occurred while processing your order: {str(e)}')
        else:
            print(f"DEBUG: Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CheckoutForm()
        print("DEBUG: GET request - showing checkout form")

    return render(request, 'checkout.html', {
        'cart': cart,
        'form': form
    })


@login_required
def order_success(request, order_id):
    print(f"DEBUG: order_success view called with order_id {order_id}")
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        print(f"DEBUG: Found order #{order.id} for user {request.user.username}")
        return render(request, 'order_success.html', {'order': order})
    except Exception as e:
        print(f"DEBUG: Error in order_success: {e}")
        messages.error(request, f'Order not found: {e}')
        return redirect('home')


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
    total_products = Product.objects.count()

    # Recent orders
    recent_orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')[:10]

    # Additional stats
    categories = Category.objects.all()
    active_carts = Cart.objects.count()

    # Today's orders
    from datetime import date
    today = date.today()
    today_orders = Order.objects.filter(created_at__date=today).count()

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'total_products': total_products,
        'recent_orders': recent_orders,
        'categories': categories,
        'active_carts': active_carts,
        'today_orders': today_orders,
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
