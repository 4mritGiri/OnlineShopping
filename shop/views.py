from django.shortcuts import render , redirect , get_object_or_404
from django.views.generic.edit import UpdateView 
from django.views.generic import DetailView , ListView 
from .models import *
from .forms import ProfileForm , PriceFilter , CheckoutForm 
from django.http import  HttpResponse , HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required 
from django.contrib import messages
from django.urls import  reverse_lazy , reverse
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Count
from django.db.models import Q

from config import settings
from django.core.mail import send_mail, EmailMessage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from . tokens import generateToken


SHIPPING_COST = 100

def register(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        confirmpwd = request.POST['comfirmpwd']
        username = request.POST['username']
        
        if User.objects.filter(email = email).exists():
            messages.error(request, 'This email has an account.')
            return redirect('register')

        if password != confirmpwd:
            messages.error(request, 'The password did not match! ')  
            return redirect('register')                  
        
        try:
            my_user = User.objects.create_user(username = username ,email = email, password = password)
            my_user.is_active = False
            my_user.save()
            messages.success(request, 'Your account has been successfully created. we have sent you an email You must comfirm in order to activate your account.')
            
        except:
            messages.error(request, 'This username has an account.')
            return redirect('register')
        
        # send email when account has been created successfully
        subject = "Welcome to online shopping"
        message = "Welcome "+ my_user.email + "\n thank for chosing out online shopping.\n To order login you need to comfirm your email account.\n thanks\n\n\n Nep X. Infotech"
        
        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)

        # send the the confirmation email
        current_site = get_current_site(request) 
        email_suject = "confirm your email"
        messageConfirm = render_to_string("emailConfimation.html", {
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(my_user.pk)),
            'token': generateToken.make_token(my_user),
            'user': my_user
        })       

        email = EmailMessage(
            email_suject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [my_user.email]
        )
        email.fail_silently = False
        email.send()
        return redirect('login')
    
    breadcrumb = [
        {'title':'Home','url': reverse('index')},
        {'title':'Account Register'}
    ]
    return render(request, 'account-register.html', {'breadcrumb': breadcrumb})    



class Login(LoginView):
    template_name = 'account-login.html'

    def get_success_url(self):
        user=self.request.user

        if user.is_superuser and user.is_staff:
            return reverse('dashboard')
        else:
            return reverse('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super(Login, self).get_context_data(**kwargs)
        context.update({
            'title': 'Account Login',
            'breadcrumb': [
                {'title':'Home','url': reverse('index')},
                {'title':'Account Login'}
            ],
        })
        return context



@login_required(login_url="login")
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect('login')



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        my_user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        my_user = None

    if my_user is not None and generateToken.check_token(my_user, token):
        my_user.is_active  = True        
        my_user.save()
        messages.success(request, "You are account is activated you can login by filling the form below.")
        return redirect("login")
    else:
        messages.success(request, 'Activation failed please try again')
        return redirect('register')



class Profile(LoginRequiredMixin , UpdateView):
    import json
    model = User
    template_name = 'account-profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('profile')
    
    def get_context_data(self, **kwargs):
        context = super(Profile, self).get_context_data(**kwargs)
        context.update({
            'breadcrumb': [
                {'title':'Home','url': reverse('index')},
                {'title':'Account','url': reverse('profile')},
                {'title':'Edit Profile'}
            ],
            'title': f'{self.request.user.username} Profile',
        })
        return context
    
    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)


class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'index.html'
    paginate_by = 12

    def post(self ,request, *args, **kwargs):
        product_id = request.POST.get('product')
        if request.user.is_authenticated:
            if 'addCart' in request.POST:
                color_id = request.POST.get('Color')
                seller_id = request.POST.get('Seller')
                size_id = request.POST.get('Size')
                material_id  = request.POST.get('Material')
                UsersProducts = Cart.objects.filter(user=request.user, payed = 'F')
                Found = False
                for i in UsersProducts:
                    if i.seller == ProductInstance.objects.get(id=seller_id) and \
                        i.size == ProductSize.objects.get(id=size_id) and \
                        i.material == Materials.objects.get(id=material_id) and \
                        i.color == Color.objects.get(id=color_id):
                        i.count += 1
                        i.save()
                        Found = True
                        break

                if not Found:    
                    addCart = Cart.objects.create(
                        user= request.user, 
                        product = Product.objects.get(id=product_id),
                        size = ProductSize.objects.get(id=size_id),
                        color= Color.objects.get(id=color_id),
                        material = Materials.objects.get(id=material_id),
                        seller=ProductInstance.objects.get(id=seller_id)
                    )
                return redirect(request.META['HTTP_REFERER'])

            elif 'addWishlist' in request.POST:
                product_id = request.POST['product']
                product_check = Product.objects.get(id=product_id)
                if product_check:
                    product= WishList.objects.filter(
                        user=request.user , 
                        product = Product.objects.get(id=product_id)
                    )
                    if product :
                        product.delete()
                        return redirect(request.META['HTTP_REFERER'])
                    else:
                        w = WishList.objects.create(
                            user=request.user , 
                            product = Product.objects.get(id=product_id)
                        )
                        w.save()
                        return redirect(request.META['HTTP_REFERER'])
                else:
                    return redirect(request.META['HTTP_REFERER'])
            

            elif 'addCompare' in request.POST:
                product_id = request.POST['product']
                product_check = Product.objects.get(id = product_id)
                if product_check:
                    product= Compare.objects.filter(
                        user=request.user , 
                        product=Product.objects.get(id = product_id)
                    )
                    if product :
                        product.delete()
                        return redirect(request.META['HTTP_REFERER'])
                    else:
                        w = Compare.objects.create(
                            user=request.user , 
                            product_id=product_id
                        )
                        w.save()
                        return redirect(request.META['HTTP_REFERER'])
                else:
                    return redirect(request.META['HTTP_REFERER'])

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        mostSold = Cart.objects.annotate(num_products=Count('seller')).order_by('-num_products')
        instock = ProductInstance.objects.filter(~Q(instock=0)).values() 

        # Show the top 9 categories most products
        topCategories = ProductCategory.objects.annotate(num_products=Count('products')).order_by('-num_products')[:9]
        context.update({
            'products': Product.objects.all(),
            'mostSold' : mostSold,
            'instock' : instock,
            'Brands': Brand.objects.all(),
            'posts' : Post.objects.all(),
            'carouselBanners' : CarouselBanner.objects.all(),
            'topCategories' : topCategories,
        })
        return context


def ProductDetailView(request, productslug):
    k = get_object_or_404(Product, slug = productslug)
    aProduct = Product.objects.filter(category = k.category)
    comments = Comments.objects.filter(product__id = k.id)

    inst = []
    i = ProductInstance.objects.filter(product = k)
    for a in i:
        if a.instock != 0:
            inst.append(a)

    if request.user.is_authenticated:
        is_authenticated = True
    else:
            is_authenticated = False

    if request.method == 'POST':
        if request.user.is_authenticated:
                if 'addComment' in request.POST:
                    text = request.POST['text']
                    c = Comments.objects.create(writer = request.user, body = text, product = k)
                    c.save()

                elif 'addCart' in request.POST:
                    try:
                        color_id = request.POST.get('Color')
                        seller_id = request.POST.get('Seller')
                        size_id = request.POST.get('Size')
                        material_id  = request.POST.get('Material')
                        UsersProducts = Cart.objects.filter(user = request.user, payed = 'F')
                        Found = False
                        for i in UsersProducts:
                            if i.seller == ProductInstance.objects.get(id=seller_id) and \
                                i.size == ProductSize.objects.get(id=size_id) and \
                                i.material == Materials.objects.get(id=material_id) and \
                                i.color == Color.objects.get(id=color_id):
                                i.count += 1
                                i.save()
                                Found = True
                                break

                        if not Found:    
                            addCart = Cart.objects.create(
                                user = request.user, 
                                product = k,
                                size = ProductSize.objects.get(id=size_id),
                                color= Color.objects.get(id=color_id),
                                material = Materials.objects.get(id=material_id),
                                seller= ProductInstance.objects.get(id=seller_id)
                            )
                            messages.success(request, "Product added to cart")
                            return redirect(request.META['HTTP_REFERER'])
                    except ObjectDoesNotExist:
                        messages.warning(request,("Please select the product details and try again"))
                        return redirect(request.META['HTTP_REFERER'])
                
                elif 'addWishlist' in request.POST:
                    product_id = request.POST['product']
                    product_check = Product.objects.get(id = product_id)
                    if product_check:
                        product= WishList.objects.filter(user=request.user , product_id = product_id )
                        if product :
                            product.delete()
                            return redirect(request.META['HTTP_REFERER'])
                        else:
                            w = WishList.objects.create(user = request.user , product_id = product_id)
                            w.save()
                            messages.success(request, "Product added to wishlist")
                            return redirect(request.META['HTTP_REFERER'])
                    else:
                        messages.warning(request, "Product not found")
                        return redirect(request.META['HTTP_REFERER'])

                elif 'addCompare' in request.POST:
                    product_id = request.POST['product']
                    product_check = Product.objects.get(id = product_id)
                    if product_check:
                        product= Compare.objects.filter(user=request.user , product_id = product_id )
                        if product :
                            product.delete()
                            return redirect(request.META['HTTP_REFERER'])
                        else:
                            w = Compare.objects.create(user = request.user , product_id = product_id)
                            w.save()
                            messages.success(request, "Product added to compare")
                            return redirect(request.META['HTTP_REFERER'])
                    else:
                        messages.warning(request, "Product not found")
                        return redirect(request.META['HTTP_REFERER'])
            

    if inst:
        context = {
            'title': f'{k.name} - {k.name}',
            'product' : k,
            'Allproduct' : aProduct,
            'comments' : comments,
            'inst' : inst,
            'is_authenticated' : is_authenticated,
            'finst': inst[0],
            'breadcrumb':[
                {'title':'Home','url': reverse('index')},
                {'title': k.category.name, 'url': reverse('CategoryListView', kwargs={'catslug' : k.category.slug})},
                {'title': k.name}
            ]
        }
    else:
        context = {
            'title': f'{k.name} - {k.name}',
            'product' : k,
            'Allproduct' : aProduct,
            'comments' : comments,
            'is_authenticated' : is_authenticated,
            'breadcrumb':[
                {'title':'Home','url': reverse('index')},
                {'title': k.category.name, 'url': reverse('CategoryListView', kwargs={'catslug' : k.category.slug})},
                {'title': k.name}
            ]
        }
    return render(request, 'product.html', context)



def CategoryOrInstockSluger(catslug):
    productsCat = get_object_or_404(ProductCategory, slug=catslug)
    products = productsCat.products.all()
    cate = productsCat
    return products, cate



def JustInstock(products):
    lstProducts = []
    for i in products:
        if i.productinst.filter(~Q(instock = 0)):
            lstProducts.append(i)
    return lstProducts



def MaxMinPrice(products, minPrice, maxPrice):
    lstProducts = []
    for i in products:
        if i.productinst.filter(~Q(instock = 0)):
            if i.productinst.filter(price__lte = maxPrice):
                if len(i.productinst.filter(price__gt = minPrice)):
                    lstProducts.append(i)
    return lstProducts



class CategoryListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop-grid.html'
    paginate_by = 12
    queryset = Product.objects.all() 

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('CategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
        return HttpResponseRedirect(reverse('CategoryListViewInstock', kwargs={'catslug' : self.kwargs['catslug']}))

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        catslug = self.kwargs['catslug']
        lst = CategoryOrInstockSluger(catslug)
        form = PriceFilter()
        color = Color.objects.all()
        mostSold = Cart.objects.annotate(num_products = Count('seller')).order_by('-num_products')
        context.update({
            'title': f'{lst[1].name} - {lst[0].count()} Products',
            'products' : lst[0],
            'cate' : lst[1],
            'brands' : Brand.objects.all(),
            'mostSold' : mostSold,
            'form' : form,
            'colors' : color,
            'is_authenticated' : self.request.user.is_authenticated,
            'breadcrumb':[
                {'title':'Home','url': reverse('index')},
                {'title': lst[1].name}
            ]
        })
        return context



class CategoryListViewInstock(CategoryListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('CategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
        return HttpResponseRedirect(reverse('CategoryListViewInstock', kwargs={'catslug' : self.kwargs['catslug']}))
        
    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        catslug = self.kwargs['catslug']
        lst = CategoryOrInstockSluger(catslug)
        form = PriceFilter()
        products = JustInstock(lst[0])
        mostSold = Cart.objects.annotate(num_products = Count('seller')).order_by('-num_products')[:5]
        context.update({
            'title': f'{lst[1].name} - {lst[1].name}',
            'products' : products,
            'cate' : lst[1],
            'brands' : Brand.objects.all(),
            'mostSold' : mostSold,
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : form,
            'breadcrumb':[
                {'title':'Home','url': reverse('index')},
                {'title': lst[1].name}
            ]
        }) 
        return context



class CategoryPriceFilterListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('CategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
        return HttpResponseRedirect(reverse('CategoryListViewInstock', kwargs={'catslug' : self.kwargs['catslug']}))
  
    def get_context_data(self, **kwargs):
        context = super(CategoryPriceFilterListView, self).get_context_data(**kwargs)
        minPrice = int(self.kwargs['minPrice'])
        maxPrice = int(self.kwargs['maxPrice'])
        lst = CategoryOrInstockSluger(self.kwargs['catslug'])
        products = MaxMinPrice(lst[0], minPrice, maxPrice)
        form = PriceFilter()
        mostSold = Cart.objects.annotate(num_products = Count('seller')).order_by('-num_products')[:5]
        context.update({
            'title': f'{lst[1].name} - {products.count()} Products',
            'products' : products,
            'cate' : lst[1],
            'brands' : Brand.objects.all(),
            'mostSold' : mostSold,
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : form,
            
            'breadcrumb':[
                {'title':'Home','url': reverse('index')},
                {'title': lst[1].name}
            ]
        })
        return context
    

class BrandListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandPriceFilter', kwargs={'brandslug' : self.kwargs['brandslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
        
    def get_context_data(self, **kwargs):
        context = super(BrandListView, self).get_context_data(**kwargs)
        maker = get_object_or_404(Brand, slug = self.kwargs["brandslug"])
        products = maker.products.all()
        mostSold = Cart.objects.annotate(num_products = Count('seller')).order_by('-num_products')[:5]
        context.update({
            'title': f'{maker.name} - {products.count()} Products',
            'products' : products,
            'brand': maker,
            'mostSold' : mostSold,
            'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
            
            'breadcrumb':[
                {'title':'Home','url': reverse('index')},
                {'title': maker.name}
            ]
        })
        return context

class BrandListViewInstock(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandPriceFilter', kwargs={'brandslug' : self.kwargs['brandslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
        
    def get_context_data(self, **kwargs):
        context = super(BrandListViewInstock, self).get_context_data(**kwargs)
        maker = get_object_or_404(Brand, slug = self.kwargs["brandslug"])
        products = JustInstock(maker.manufactor.all())
        mostSold = Cart.objects.annotate(num_products = Count('seller')).order_by('-num_products')[:5]
        context.update({
            'title': f'{maker.name} - {maker.name}',
            'products' : products,
            'brand': maker,
            'mostSold' : mostSold,
            'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
        })
        return context

class BrandPriceFilter(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandPriceFilter', kwargs={'brandslug' : self.kwargs['brandslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
     
    def get_context_data(self, **kwargs):
        context = super(BrandPriceFilter, self).get_context_data(**kwargs)
        maker = get_object_or_404(Brand, slug = self.kwargs["brandslug"])
        products = MaxMinPrice(maker.manufactor.all(), self.kwargs['minPrice'], self.kwargs['maxPrice'])
        mostSold = Cart.objects.annotate(num_products = Count('seller')).order_by('-num_products')[:5]
        context.update({
            'title': f'{maker.name} - {maker.name}',
            'products' : products,
            'brand': maker,
            'mostSold' : mostSold,
            'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
        })
        return context


def BrandCategorySluger(catslug, manu):
    productsCat = get_object_or_404(ProductCategory, slug = catslug)
    products = manu.products.filter(category = productsCat)
    cate = productsCat

    return products, cate

class BrandCategory(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandCategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'],'brandslug' : self.kwargs['brandslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
    
    def get_context_data(self, **kwargs):
        context = super(BrandCategory, self).get_context_data(**kwargs)
        brand = self.kwargs['brandslug']
        catslug = self.kwargs['catslug']
        manu = get_object_or_404(Brand, slug = brand)
        lst = BrandCategorySluger(catslug, manu)
        mostSold = Cart.objects.annotate(num_products = Count('seller')).order_by('-num_products')[:5]
        context.update({
            'title': f'{manu.name} - {lst[0].count()} Products',
            'products' : lst[0],
            'cate' : lst[1],
            'mostSold' : mostSold,
            'brand': manu,
            # 'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
        })
        return context

class BrandCategoryInstock(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandCategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'],'brandslug' : self.kwargs['brandslug'],'minPrice' : minPrice, 'maxPrice' : maxPrice}))
    
    def get_context_data(self, **kwargs):
        context = super(BrandCategoryInstock, self).get_context_data(**kwargs)
        brand = self.kwargs['brandslug']
        catslug = self.kwargs['catslug']
        manu = get_object_or_404(Brand, slug = brand)
        lst = BrandCategorySluger(catslug, manu)
        products = JustInstock(lst[0])
        mostSold = Cart.objects.annotate(num_products = Count('seller')).order_by('-num_products')
        context.update({
            'title': f'{manu.name} - {lst[1].count()} Products',
            'products' : products,
            'cate' : lst[1],
            'mostSold' : mostSold,
            'brand': manu,
            'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
        })
        return context

class BrandCategoryPriceFilter(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop-grid.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        form = PriceFilter(request.POST)
        if form.is_valid():
            minPrice = form.cleaned_data['minPrice']
            maxPrice = form.cleaned_data['maxPrice']
            return HttpResponseRedirect(reverse('BrandCategoryPriceFilter', kwargs={'catslug' : self.kwargs['catslug'], 'brandslug' : self.kwargs['brandslug'], 'minPrice' : minPrice, 'maxPrice' : maxPrice}))

    def get_context_data(self, **kwargs):
        context = super(BrandCategoryPriceFilter, self).get_context_data(**kwargs)
        brand = self.kwargs['brandslug']
        catslug = self.kwargs['catslug']
        maxPrice = self.kwargs['maxPrice']
        minPrice = self.kwargs['minPrice']
        manu = get_object_or_404(Brand, slug = brand)
        lst = BrandCategorySluger(catslug, manu)
        products = MaxMinPrice(lst[0], minPrice, maxPrice)
        mostSold = Cart.objects.annotate(num_products = Count('seller')).order_by('-num_products')[:5]
        context.update({
            'title': f'{manu.name} - {lst[1].count()} Products',
            'products' : products,
            'cate' : lst[1],
            'mostSold' : mostSold,
            'brand': manu,
            'brands' : Brand.objects.all(),
            'is_authenticated' : self.request.user.is_authenticated,
            'form' : PriceFilter(),
        })
        return context

def is_authenticated(user):
    return not user.is_authenticated



@login_required(login_url="login" , )
def cart_(request):
    objs = Cart.objects.filter(user=request.user ,payed = 'F')
    tPrice = 0
    for i in objs:
        tPrice += i.total()
    final = 0
    for i in objs:
        final += i.total_price()
    CFinal = 0
    for i in objs:
        CFinal += i.final_price()
    
    tax = final - tPrice  
    coupon = CFinal - final  
    sendCost = SHIPPING_COST * len(objs)
    toPay = CFinal + tax + sendCost
    print(toPay)

    if objs:
        if request.method == 'POST':
            if 'update' in request.POST:
                slug = request.POST.get('product_slug')
                count = request.POST.get('quantity')
                product_obj = Product.objects.get(slug = slug)
                for obj in objs:
                    if obj.product == product_obj:
                        obj.count = int(count)
                        obj.save()
                        break
            if 'delete' in request.POST:
                slug = request.POST.get('product_slug')
                count = request.POST.get('quantity')
                product_obj = Product.objects.get(slug = slug)
                for obj in objs:
                    if obj.product == product_obj:
                        print('-----   Found : True   -----')
                        obj.delete()
                        break
                return redirect(request.META['HTTP_REFERER'])

            if 'applyCoupon' in request.POST:
                code = request.POST.get('couponCode')
                error = None
                try:
                    co = Coupon.objects.get(code = code)
                    if co.is_expired():
                        error = 'The expiration date for this coupon has expired!'
                    elif not co.count > 0:
                        error = 'The number of uses for this coupon has expired!'
                    else:
                        for obj in objs:
                            obj.coupon = co
                            obj.save()
                        return HttpResponseRedirect(reverse('cart'))
                except Coupon.DoesNotExist:
                    error = 'The coupon code is incorrect!'
                
                if error != None:
                    context = {
                        'title': f'Shopping Cart',
                        'carts' : objs,
                        'is_authenticated' : True,
                        'error' : error,
                        'breadcrumb':[
                            {'title':'Home','url': reverse('index')},
                            {'title': "Shopping Cart", 'url': reverse('cart')},
                            {'title':'Shopping Cart'}
                        ]
                    }
                return render(request, 'cart.html', context)
            
        
        context = {
            'title': f'Cart({objs.count()})',
            'carts' : objs,
            'is_authenticated' : True,
            'totalPrice': tPrice,
            'finalPrice' : final,
            'tax' : tax,
            'coupon': coupon,
            'sendCost' : sendCost,
            'toPay': toPay,
            'breadcrumb':[
                {'title':'Home','url': reverse('index')},
                {'title': "Shopping Cart", 'url': reverse('cart')},
                {'title':'Cart'}
            ]
        }
        return render(request, 'cart.html', context)
    else:
        context = {
            'title': f'Empty Cart',
            'breadcrumb':[
                {'title':'Home','url': reverse('index')},
                {'title': "Shopping Cart", 'url': reverse('cart')},
                {'title':'Empty Cart'}
            ]
        }
        return render(request, 'cart-empty.html', context)


def contact_us(request):
    context = {}
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        description = request.POST['description']
        call = ContactUs.objects.create(name = name, email = email, desc = description)
        call.save()
        context = {
            'title': 'Contact Us',
            'sent' : True,
        }
    return render(request, 'contact-us.html', context)


from django.contrib.auth import get_user_model


@login_required(login_url="login")
def checkout(request):
    User = get_user_model()
    try:
        usr = User.objects.get(username=request.user.username)
    except User.DoesNotExist:
        messages.error(request, "User does not exist. Please log in again.")
        return redirect('login')

    carts = Cart.objects.filter(user=request.user, payed='F')

    # Calculate prices
    tPrice = sum(i.total() for i in carts)
    final = sum(i.total_price() for i in carts)
    CFinal = sum(i.final_price() for i in carts)
    
    tax = final - tPrice  
    coupon = CFinal - final  
    sendCost = SHIPPING_COST * len(carts)
    toPay = CFinal + tax + sendCost

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Process the form data
            company = form.cleaned_data['company']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            postcode = form.cleaned_data['postcode']
            state = form.cleaned_data['state'] 
            description = form.cleaned_data['desc']  
            sell = Sold.objects.create(
                user=request.user, company=company,
                address=address, zip_code=postcode,
                state=States.objects.get(id=state),
                city=city, total_price=CFinal, send_price=sendCost, tax=tax,
                total=toPay, desc=description
            )
                
            for c in carts:
                sell.products.add(c)
                instance = c.seller
                instance.instock -= 1
                instance.save()
                c.payed = 'T'
                c.save()

            sell.save()
            messages.success(request, "Order placed successfully")
            return redirect('cart')
        else:
            print("Form is not valid")  # Debugging line
            print(form.errors)  # Debugging line to show form errors
        
    else:
        form = CheckoutForm(initial={'address': usr.address, 'city': usr.city, 'state': usr.state, 'postcode': usr.postcode})
    
    context = {
        'title': f'Checkout({usr.username})',
        'form': form,
        'state': States.objects.all(),
        'not_authenticated': False,
        'carts': carts,
        'totalPrice': tPrice,
        'finalPrice': final,
        'tax': tax,
        'coupon': coupon,
        'sendCost': sendCost,
        'toPay': toPay,
        'is_authenticated': True,
        'usr': usr,
        'breadcrumb': [
            {'title': 'Home', 'url': reverse('index')},
            {'title': 'Shopping Cart', 'url': reverse('cart')},
            {'title': 'Checkout'}
        ]
    }
    return render(request, 'checkout.html', context)



class PostListView(ListView):
    model = Post
    template_name = 'blog-classic.html'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        # use paginator to get the posts
        posts = Post.objects.all()
        paginator = Paginator(posts, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        context.update({
            'posts' : posts,
            'title': 'Blogs',
            'tags': Tag.objects.all(),
            'breadcrumb':[
                {'title':'Home','url': reverse('index')},
                {'title':'Blogs'}
            ]
        })
        return context


class LatestPostsMixin(object):

    def get_context_data(self, **kwargs):
        context = super(LatestPostsMixin, self).get_context_data(**kwargs)
        try:
            context['latest_posts_list'] =  Post.objects.all()
        except:
            pass
        return context


class PostDetailView(LatestPostsMixin,DetailView):
    model = Post
    template_name = 'post.html'
    slug = 'slug'
    
    # get the post and the related posts
    def get_object(self):
        return get_object_or_404(Post, slug=self.kwargs['slug'])
    
    def get_related_posts(self):
        # Don't show the post itself in the related posts
        return Post.objects.filter(~Q(slug=self.kwargs['slug'])).order_by('-published_date')[:4]
    
    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        
        comments = self.object.comments.filter(status=Comments.StatusChoice.OK).order_by('date')
        
        context.update({
            'title': self.object.title,
            'tags': Tag.objects.all(),
            'latest_posts_list': Post.objects.all(),
            'related_posts': self.get_related_posts(),
            'comments': comments,
            'breadcrumb':[
                {'title':'Home','url': reverse('index')},
                {'title':'Blogs', 'url': reverse('blog')},
                {'title':self.object.title}
            ]
        })
        return context
    


class Address(LoginRequiredMixin,DetailView):
    model = User
    template_name = 'account-addresses.html'
    
    def get_context_data(self, **kwargs):
        context = super(Address, self).get_context_data(**kwargs)
        context.update({
            'title': 'Addresses',
            'breadcrumb':[
                {'title':'Home','url': reverse('index')},
                {'title':'Addresses'}
            ]
        })
        return context

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk )



"""from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

def search_post(request , search=None):
    if request.method =='POST':
        user_search = request.POST.get('search')
        
        if user_search:
            post_results1 = Post.objects.filter(body__icontains= user_search)
            post_results2 = Post.objects.filter(title__icontains= user_search)
            posts = post_results1 | post_results2

            if search:
                posts.filter(slug__in= search)
            
            paginator = Paginator(posts , 6)
            page = request.GET.get('page')

            try:
                posts = paginator.page(page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            
            return render(request , 'blog-classic.html' , {'posts':posts , 'page':page })
    
    post_results = Post.objects.all()
    posts = post_results
    if search:
        posts.filter(slug__in= search)
        
    paginator = Paginator(posts , 6)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request , 'blog-classic.html' , {'posts':posts , 'page':page })
"""




from functools import reduce
import operator

class SearchProduct(ProductListView):
    """
        Display a Product List  filtered by search query
    """
    paginate_by = 12
    template_name = 'shop-grid.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        result = super(SearchProduct, self).get_queryset()
        query = self.request.GET.get('search')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                (Q(name__icontains = q) for q in query_list))
            )
        return result

    def get_context_data(self, **kwargs):
        context = super(SearchProduct, self).get_context_data(**kwargs)
        mostSold = Cart.objects.annotate(num_products = Count('seller')).order_by('-num_products')[:5]
        context.update({
            'is_authenticated' : self.request.user.is_authenticated,
            'mostSold' : mostSold,
            'color':Color.objects.all(),
            'title': "Search",
        })
        return context

    def reduce(func, items):
        result = items.pop()
        for item in items:
            result = func(result, item)
        return result       
    
    def and_(a, b):
        return a and b


@login_required(login_url='login')
def compare(request):
    compare = Compare.objects.filter(user=request.user)
    product = []

    for p in compare:
        product_detail = ProductInstance.objects.filter(product__slug=p.product.slug)
        for a in product_detail:
            product.append(a) 

    if request.method == 'POST':
        if 'delete' in request.POST:
            slug = request.POST.get('product_slug')
            product_obj = Product.objects.get(slug=slug)
            for obj in compare:
                if obj.product == product_obj:
                    print('-----   Found : True   -----')
                    obj.delete()
                    break
        return redirect(request.META['HTTP_REFERER'])


    context = {
        'title': 'Compare',
        'compare':compare,
        'detail':product,
        'breadcrumb':[
            {'title':'Home','url': reverse('index')},
            {'title':'Compare'}
        ]
    }
    return render(request , 'compare.html' , context)



def error_404(request , *args ,**kwargs):
    context = {
        'title': '404',
    }
    return render(request ,'404.html' , context)

def error_500(request , *args ,**kwargs):
    context = {
        'title': '500',
    }
    return render(request ,'500.html' , context)

def about_us(request):
    context = {
        'title': 'About Us',
    }
    return render(request ,'about-us.html' , context)


from django.core.paginator import Paginator ,EmptyPage, PageNotAnInteger
@login_required(login_url="login")
def account_orders(request):
    cart = Cart.objects.filter(user=request.user, payed = 'T')
    page = request.GET.get('page', 1)
    paginator = Paginator(cart, 5)
    try:
        carts = paginator.page(page)
    except PageNotAnInteger:
        carts = paginator.page(1)
    except EmptyPage:
        carts = paginator.page(paginator.num_pages)

    sold = []
    for product in cart:
        sold.append(product)
    
    reverse_list = sold[::-1]
    context = {
        'title': 'Orders ({} Items)'.format(len(reverse_list)),
        'sold':reverse_list,
        'page_obj': carts,
        'breadcrumb':[
            {'title':'Home','url': reverse('index')},
            {'title':'Orders'}
        ]
    }
    return render(request ,'account-orders.html' , context)



def brands(request):
    context = {
        'title': 'Brands',
        'brands' : Brand.objects.all(),
        'breadcrumb':[
            {'title':'Home','url': reverse('index')},
            {'title':'Brands'}
        ]
    }
    return render(request ,'brands.html' , context)


def faq(request):
    context = {
        'title': 'FAQ',
    }
    return render(request ,'faq.html' , context)



@login_required
def account_dashboard(request):
    cart = Cart.objects.filter(user=request.user, payed='T')
    sold = []
    for product in cart:
        sold.append(product)
    
    reverse_list = sold[::-1]
    lenSold = len(reverse_list)//2
    context = {
        'title': 'Dashboard',
        'sold':reverse_list,
        'lenSold': lenSold,
        'breadcrumb':[
            {'title':'Home','url': reverse('index')},
            {'title':'Dashboard'}
        ]
    }
    return render(request ,'account-dashboard.html' , context)



def terms_and_conditions(request):
    context = {
        'title': 'Terms and Conditions',
        'breadcrumb':[
            {'title':'Home','url': reverse('index')},
            {'title':'Terms and Conditions', 'url': reverse('terms_and_conditions')},
            {'title':'Terms and Conditions'}
        ]
    }
    return render(request ,'terms-and-conditions.html' , context)


@login_required(login_url="login")
def track_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        username = request.POST.get('username')
        user = User.objects.get(username=username)
        try:
            order = Sold.objects.get(id=order_id, user=user)
            context = {
                'title': 'Track Order',
                'order': order,
                'breadcrumb':[
                    {'title':'Home','url': reverse('index')},
                    {'title':'Track Order', 'url': reverse('track_order')},
                    {'title':f'{request.user.username}'}
                ]
            }
            return render(request, 'track-order.html', context)
        except Sold.DoesNotExist:
            messages.error(request, "Order not found. Please check your order ID and username.")
            return redirect('track_order')
        
        
    context = {
        'title': 'Track Order',
        'breadcrumb':[
            {'title':'Home','url': reverse('index')},
            {'title':'Track Order', 'url': reverse('track_order')},
            {'title':f'{request.user.username}'}
        ]
    }
    return render(request ,'track-order.html' , context)



@login_required(login_url='login')
def wishlist(request):
    wishlist = WishList.objects.filter(user=request.user)
    product = []

    for p in wishlist:
        product_detail = ProductInstance.objects.filter(product__slug=p.product.slug)
        for a in product_detail:
            product.append(a)

    if request.method == 'POST':
        if 'delete' in request.POST:
            slug = request.POST.get('product_slug')
            try:
                product_obj = Product.objects.get(slug=slug)
                for obj in wishlist:
                    if obj.product == product_obj:
                        print('-----   Found : True   -----')
                        obj.delete()
                        break
            except Product.DoesNotExist:
                messages.error(request, "Product not found. It may have been removed from the wishlist.")
        
        elif 'addCart' in request.POST:
            print('-----   addCart : True   -----')
            slug = request.POST.get('product_slug')
            try:
                product_obj = Product.objects.get(slug=slug)
                cart = Cart.objects.create(user=request.user, product=product_obj, count=1)
                cart.save()
                messages.success(request, "Product added to cart successfully")
            except Product.DoesNotExist:
                messages.error(request, "Product not found. Unable to add to cart.")

        return redirect(request.META['HTTP_REFERER'])

    context = {
        'title': 'Wishlist',
        'wishlist': wishlist,
        'detail': product,
        'breadcrumb': [
            {'title': 'Home', 'url': reverse('index')},
            {'title': 'Wishlist', 'url': reverse('wishlist')},
            {'title': 'Wishlist'}
        ]
    }
    return render(request, 'wishlist.html', context)

