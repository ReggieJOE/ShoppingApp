from .models import Cart

def cart_items_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            return {'cart_items_count': cart.get_total_items()}
    return {'cart_items_count': 0}