from django.urls import path
from .views import *
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView
)
from django.urls import reverse_lazy



urlpatterns =[
    path('',ProductListView.as_view(), name='index'),

    # Authentication urls
    path('signup', register, name='register'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('password_change/', PasswordChangeView.as_view(
            template_name='account-password.html',
            success_url=reverse_lazy('password_change_done'),
            extra_context={
                'title':'Change Password', 
                'breadcrumb':[
                    {'title':'Home','url': reverse_lazy('index')},
                    {'title':'Track Order','url': reverse_lazy('track_order')},
                    {'title':'Change Password'}
                ]
            }
        ), 
        name='change-password',
    ),
    path('password_change/done/', PasswordChangeDoneView.as_view(
            template_name='password_change_done.html',
        ),
        name='password_change_done',
    ),
    
    # Product urls
    path('product/<slug:productslug>/', ProductDetailView, name='ProductDetailView'),
    path('search/', SearchProduct.as_view(), name ='search_product'),
    
    path('category/<slug:catslug>/', CategoryListView.as_view(), name='CategoryListView'),
    path('category/<slug:catslug>/instock/', CategoryListViewInstock.as_view(), name='CategoryInstock'),
    path('category/<slug:catslug>/instock/<int:minPrice>/<int:maxPrice>/', CategoryPriceFilterListView.as_view(), name='CategoryPriceFilter'),
    path('category/<slug:catslug>/<slug:brandslug>/', BrandCategory.as_view(), name= 'BrandCategory'),
    path('category/<slug:catslug>/<slug:brandslug>/instock/', BrandCategoryInstock.as_view(), name= 'BrandCategoryInstock'),
    path('category/<slug:catslug>/<slug:brandslug>/instock/<int:minPrice>/<int:maxPrice>/', BrandCategoryPriceFilter.as_view(), name= 'BrandCategoryPriceFilter'),

    path('brands/<slug:brandslug>/', BrandListView.as_view(), name='BrandListView'),
    path('brands/<slug:brandslug>/instock/', BrandListViewInstock.as_view(), name='BrandListViewInstock'),
    path('brands/<slug:brandslug>/instock/<int:minPrice>/<int:maxPrice>/', BrandPriceFilter.as_view(), name='BrandPriceFilter'),
    path('brands/', brands, name='brands'),

    path('compare/', compare, name='compare'),
    path('wishlist/', wishlist, name='wishlist'),
    path('cart/', cart_, name='cart'),
    path('orders/', account_orders, name='orders'),
    path('checkout/', checkout, name='checkout'),
    path('update/cart/', update_cart, name='update_cart'),
    path('track_order/', track_order, name='track_order'),
    #path('cart/cart-empty/',cart_empty, name="cart-empty" ),

    path('dashboard/', account_dashboard, name='dashboard'), 
    path('profile/', Profile.as_view(), name='profile'),
    path('address/', Address.as_view(), name='addresses'),
    path('blog/', PostListView.as_view(), name='blog'),
    path('blog/post/<slug:slug>/', PostDetailView.as_view(), name='PostDetailView'),
    #path('blog/search/', search_post, name='search_post'),

    path('about_us/', about_us, name='about-us'),
    path('contact-us/', contact_us, name='contact-us'),
    path('faq/', faq, name='faq'),
    path('terms_and_conditions/', terms_and_conditions, name='terms_and_conditions'),
]



handler404=error_404
handler500=error_500
