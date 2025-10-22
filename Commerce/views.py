from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .forms import UserRegisterForm, CheckoutForm, ProductForm
from django.contrib.auth import logout as auth_logout
from django.db.models import Sum, Count, Max, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


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
    return (render(request, 'cart.html', {'cart': cart}))

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
    # FIXED: Proper indentation for return statement
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


# FIXED: Added staff_required decorator function
def staff_required(function=None):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('home')
        return function(request, *args, **kwargs)

    return wrapper


@login_required
@staff_required
def admin_dashboard(request):
    # Statistics
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_customers = User.objects.filter(is_staff=False).count()
    total_products = Product.objects.count()

    # Recent orders
    recent_orders = Order.objects.select_related('user').prefetch_related('items__product').order_by(
        '-created_at')[:10]

    # Recent users and top customers
    recent_users = User.objects.filter(is_staff=False).order_by('-date_joined')[:5]
    top_customers = User.objects.filter(
        order__isnull=False
    ).annotate(
        total_orders=Count('order'),
        total_spent=Sum('order__total_amount')
    ).order_by('-total_spent')[:5]

    # Additional stats
    categories = Category.objects.all()
    active_carts = Cart.objects.count()

    # Today's orders
    from datetime import date
    today = date.today()
    today_orders = Order.objects.filter(created_at__date=today).count()

    # Low stock products
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

    return render(request, 'admin_dashboard.html', context)


@login_required
@staff_required
def user_order_history(request, user_id):
    """View detailed order history for a specific user"""
    try:
        user = User.objects.get(id=user_id)
        orders = Order.objects.filter(user=user).select_related('user').prefetch_related(
            'items__product').order_by('-created_at')

        # Calculate user statistics
        total_orders = orders.count()
        total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        avg_order_value = total_spent / total_orders if total_orders > 0 else 0

        context = {
            'user_profile': user,
            'orders': orders,
            'total_orders': total_orders,
            'total_spent': total_spent,
            'avg_order_value': avg_order_value,
        }
        return render(request, 'admin/user_order_history.html', context)

    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('admin_dashboard')


@login_required
@staff_required
def customer_list(request):
    """View all customers with their order statistics"""
    customers = User.objects.filter(is_staff=False).annotate(
        total_orders=Count('order'),
        total_spent=Sum('order__total_amount'),
        last_order_date=Max('order__created_at')
    ).order_by('-date_joined')

    context = {
        'customers': customers,
    }
    return render(request, 'admin/customer_list.html', context)


# FIXED: Added the missing order_history view
@login_required
@staff_required
def order_history(request):
    """View all orders in the system (no user_id required)"""
    try:
        # Debug: Let's see what's available
        print("DEBUG: Starting order_history view")

        # Try different approaches to find the correct related name
        orders = Order.objects.select_related('user').order_by('-created_at')

        # Debug: Check the first order to see its structure
        if orders.exists():
            first_order = orders.first()
            print(f"DEBUG: First order ID: {first_order.id}")
            print(f"DEBUG: Order attributes: {dir(first_order)}")

            # Try to access order items
            try:
                items = first_order.items.all()
                print(f"DEBUG: Found items using 'items': {items.count()}")
            except AttributeError:
                print("DEBUG: 'items' relation not found")

            try:
                items = first_order.orderitem_set.all()
                print(f"DEBUG: Found items using 'orderitem_set': {items.count()}")
            except AttributeError:
                print("DEBUG: 'orderitem_set' relation not found")

        # Calculate statistics
        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0

        context = {
            'orders': orders,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
        }

        return render(request, 'admin/order_history.html', context)

    except Exception as e:
        print(f"DEBUG: Error in order_history: {e}")
        messages.error(request, f'Error loading order history: {str(e)}')
        return redirect('admin_dashboard')


@login_required
@staff_required
def admin_dashboard(request):
    """Admin dashboard view"""
    try:
        # Statistics - FIXED: Make sure we're calling count() on QuerySets, not functions
        total_orders = Order.objects.count()  # This should be a number, not a function
        total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        total_customers = User.objects.filter(is_staff=False).count()  # This should be a number
        total_products = Product.objects.count()  # This should be a number

        # Recent orders - FIXED: Use correct related name
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

        # Recent users and top customers
        recent_users = User.objects.filter(is_staff=False).order_by('-date_joined')[:5]
        top_customers = User.objects.filter(
            order__isnull=False
        ).annotate(
            total_orders=Count('order'),
            total_spent=Sum('order__total_amount')
        ).order_by('-total_spent')[:5]

        # Additional stats
        categories = Category.objects.all()
        active_carts = Cart.objects.count()

        # Today's orders
        from datetime import date
        today = date.today()
        today_orders = Order.objects.filter(created_at__date=today).count()

        # Low stock products
        low_stock_products = Product.objects.filter(stock__lt=10)[:5]

        context = {
            'total_orders': total_orders,  # This should be a number
            'total_revenue': total_revenue,
            'total_customers': total_customers,  # This should be a number
            'total_products': total_products,  # This should be a number
            'recent_orders': recent_orders,
            'recent_users': recent_users,
            'top_customers': top_customers,
            'categories': categories,
            'active_carts': active_carts,
            'today_orders': today_orders,
            'low_stock_products': low_stock_products,
        }

        return render(request, 'admin_dashboard.html', context)

    except Exception as e:
        print(f"DEBUG: Error in admin_dashboard: {e}")
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('home')

@login_required
@staff_required
def admin_product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" successfully updated.')
            return redirect('admin_products')
        else:
            form = ProductForm(instance=product)
        context = {
          'product' : product,
         'form': form,
        }
        return render(request, 'admin/product_detail.html', context)


@login_required
@staff_required
def admin_products(request):
    """Custom admin products view"""
    products = Product.objects.select_related('category').all()

    # Filter by category if provided
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

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'total_products': products.count(),
        'low_stock_products': products.filter(stock__lt=10).count(),
    }

    return render(request, 'admin/admin_products.html', context)


@login_required
@staff_required
def admin_product_detail(request, product_id=None):
    """Custom admin product detail view - handles both add and edit"""
    if product_id:
        # Editing existing product
        product = get_object_or_404(Product, id=product_id)
        title = f"Edit Product: {product.name}"
    else:
        # Adding new product
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

    return render(request, 'admin/product_detail.html', context)