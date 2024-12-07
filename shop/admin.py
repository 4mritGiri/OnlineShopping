from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.html import mark_safe
from shop.models import Product, ProductCategory, Brand, ProductSize, States, Color, Materials, ProductInstance, WishList, Compare, Sold, Post, Coupon, Cart, ContactUs, User, CarouselBanner, Tag, Comments, Review
from unfold.admin import ModelAdmin, TabularInline
from shop.forms import CarouselBannerForm



@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    list_display = ['profile_image' , 'email', 'first_name' , 'last_name' ,'is_staff' , 'is_active']
    
    list_display_links = ['email']
    list_editable = ['is_staff', 'is_active']
    list_filter = ['gender' , 'is_staff' , 'is_superuser' , 'is_active']
    actions = ['make_inactive']

    fieldsets = (
        (None , {'fields':('email','password')}),
        ('Personal Info',{
            'fields':(
                'first_name',
                'last_name',
                'gender',
                'age',
                'postcode',
                'avatar',
                'newsletter',
                'description',)
        }),
        ('Contact Info',{
            'fields':(
                'phone',
                'city',
                'state',
                'address',
            )
        }),

        ('Permissions',{
            'fields':(
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),

        ('Important Dates',{
            'fields':(
                'last_login', 
                'date_joined'
            )
        })
    )
    
    
    def make_inactive(self , request , queryset):
        updated=queryset.update(is_active=False)
        self.message_user(request,ngettext(
        '%d user was inactivated.',
        '%d users were inactivated.',
        updated,
        ) % updated, messages.SUCCESS)
    make_inactive.short_description ='Make inactive'


    def profile_image(self, obj):
        if obj.avatar:
            return mark_safe('<img src="{url}" width="{width}" height="{height}" />'.format(
                url = obj.avatar.url,
                width=70,
                height=70,
                )
            )
        return "No Image"



@admin.register(CarouselBanner)
class CarouselBannerAdmin(ModelAdmin):
    fields = ['title', 'subtitle', 'description', 'image', 'category']
    list_display = ['title', 'subtitle', 'description', 'image', 'category']
    search_fields = ['title', 'subtitle', 'description']



@admin.register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display =['name', 'image_preview']
    prepopulated_fields={'slug':('name',),}
    search_fields=['name']
    fields=['name', 'slug', 'image']
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="{width}" height="{height}" />'.format(
                url = obj.image.url,
                width=80,
                height=80,
                )
            )
        return "No Image"



@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ['name','logo_image']
    readonly_fields = ['logo_image']
    search_fields = ['name',]
    fields =['name','slug','logo','logo_image']
    prepopulated_fields ={'slug':('name',),}

    def logo_image(self, obj):
        if obj.logo:
            return mark_safe('<img src="{url}" width="{width}" height="{height}" />'.format(
                url = obj.logo.url,
                width=80,
                height=80,
                )
            )
        return "No Image"

    

@admin.register(ProductSize)
class ProductSizeAdmin(ModelAdmin):
    list_display = ['sizeno',]


@admin.register(Comments)
class CommentsAdmin(ModelAdmin):
    list_display = ['writer', 'body', 'created_at']


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ['writer', 'rating', 'body', 'is_active', 'created_at']



@admin.register(States)
class StatesAdmin(ModelAdmin):
    list_display = ['name','id']
    search_fields = ['name',]
    order_by =['A']



@admin.register(Color) 
class ColorAdmin(ModelAdmin):
    list_display = ['name',]
    search_fields = ['name']
    order_by =['A']



@admin.register(Materials)
class MaterialsAdmin(ModelAdmin):
    list_display=['name',]
    search_fields=['name']
    order_by =['A']



class ProductInstanceInline(TabularInline):
    model = ProductInstance
    def get_extra(self, request , obj=None , **kwargs):
        extra = 0
        return extra



@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display=['name','category','slug','brand','mini_description',]
    list_editable = ['brand',]
    list_filter=['name','category','brand','size','color','material',]
    list_display_links = ('name',)
    sortable_by = ['name','category',]
    search_fields = ['name','category','brand','color','material','size']
    prepopulated_fields = {'slug':('brand','name',)}
    fieldsets =(
        ('General Info',{
            'fields':('name','slug','brand','category',)
        }),
        ('Product Info',{
            'fields':('color','material','size','mini_description','tags')
        }),
        ('pictures',{
            'fields':('pic0','pic1','pic2','pic3','pic4',)
        }),
        (None,{'fields':('description',)}),
    ) 
    inlines=[ProductInstanceInline]



@admin.register(ProductInstance)
class ProductInstanceAdmin(ModelAdmin):
    list_display = ['product', 'seller', 'price', 'off', 'instock']
    list_filter = ['product', 'seller', 'price', 'off']
    list_display_links = ['product', 'seller']
    sortable_by = ['product', 'seller', 'price', 'off']
    search_fields = ['product', 'seller']
    list_editable = ['off', 'instock']



@admin.register(WishList)
class WishListAdmin(ModelAdmin):
    list_display = ['product', 'user', 'created_at']
    fields = ['product', 'user', 'created_at']
    readonly_fields = ['created_at']



@admin.register(Compare)
class CompareAdmin(ModelAdmin):
    list_display = ['product', 'user', 'created_at']
    fields = ['product', 'user', 'created_at']
    readonly_fields = ['created_at']



@admin.register(Sold)
class SoldAdmin(ModelAdmin):
    list_diaplay = ["user",'products','total','date','sent',]
    search_fields   = ['products','user']
    list_filter = ["user",'total','date','sent',]



@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ['name',]
    search_fields = ['name',]



@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ['title','short_description','published_date',"post_image"]
    list_filter = ['published_date']
    search_fields = ['title','short_description',]
    fields = ['title','slug','body','pic','tags','post_image' , 'published_date', 'created_by']
    prepopulated_fields = {'slug':('title',),}
    readonly_fields = ['post_image' , 'published_date']

    def post_image(self, obj):
        if obj.pic:
            return mark_safe('<img src="{url}" width="{width}" height="{height}" />'.format(
                url = obj.pic.url,
                width=200,
                height=200,
                )
            )
        return "No Image"



@admin.register(Coupon)
class CouponAdmin(ModelAdmin):
    list_display = ['code','off','count','expire',]
    list_filter = ['count' , 'off' , 'expire',]
    search_fields = ['code',]



@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ['user','product','count','seller','coupon','payed',]
    list_filter = ['product','seller','payed',]
    search_fields = ['user','seller','product',]



@admin.register(ContactUs)
class ContactUsAdmin(ModelAdmin):
    list_display = ['name' , 'email',]
    search_fields = ['name','email',]
    sortable_by = ['name','email',]
    order_by = ['name']
