from .models import Brand, ProductCategory, Cart, Compare, WishList

def global_context(request):
   brands = Brand.objects.all() or None
   categories = ProductCategory.objects.all() or None
   cart_count = Cart.objects.none()
   compare_count = Compare.objects.none()
   wishlist_count = WishList.objects.none()

   if request.user.is_authenticated:
      wishlist_count = WishList.objects.filter(user=request.user).count() or 0
      compare_count = Compare.objects.filter(user=request.user).count() or 0
      cart_count = Cart.objects.filter(user=request.user, payed = 'F').count() or 0
   else:
      wishlist_count = 0
      compare_count = 0
      cart_count = 0

      
   features = [
      {
         'icon': 'fi-free-delivery-48',
         'title': 'Free shipping',
         'subtitle': 'Free shipping for orders over Rs. 100,000'
      },
      {
         'icon': 'fi-24-hours-48',
         'title': '24 hour support',
         'subtitle': 'Call anytime'
      },
      {
         'icon': 'fi-payment-security-48',
         'title': 'Secure payments',
         'subtitle': 'Secure payments'
      },
      {
         'icon': 'fi-tag-48',
         'title': 'Hot offers',
         'subtitle': 'Discounts up to 90%',
      }
   ]
   
   
   return {
      'Brands': brands,
      'Categories': categories,
      'cart_count': cart_count,
      'compare_count': compare_count,
      'wishlist_count': wishlist_count,
      'features': features
   }