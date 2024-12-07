from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.text import slugify
from django.template.defaultfilters import truncatechars
from django.utils.translation import gettext_lazy as _
from .validators import phone_validator
from unidecode import unidecode
import random
from time import gmtime, strftime
import os



def get_upload_path(instance, filename, folder_name):
    return os.path.join(f'images/{folder_name}/', strftime("%Y%m%d-%H%M%S", gmtime()) + filename)

def get_profile_upload_path(instance, filename):
    return get_upload_path(instance, filename, 'profile')

def get_category_upload_path(instance, filename):
    return get_upload_path(instance, filename, 'categories')

def get_product_upload_path(instance, filename):
    return get_upload_path(instance, filename, 'products')

def get_brand_logo_upload_path(instance, filename):
    return get_upload_path(instance, filename, 'brand_logos')

def get_post_upload_path(instance, filename):
    return get_upload_path(instance, filename, 'posts')

def get_carousel_banner_upload_path(instance, filename):
    return get_upload_path(instance, filename, 'carousel_banners')



class States(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = ''
        verbose_name_plural = 'States'
        verbose_name = 'State'
        ordering = ['name']

    def __str__(self):
        return self.name



class User(AbstractUser):
    class GenderChoice(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        UNSET = "FM", "Unset"

    class NewsChoice(models.TextChoices):
        TRUE = 'T', 'Subscribe to the newsletter'
        FALSE = 'F', 'Not Subscribe to the newsletter'

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    age = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=20, null=True, blank=True, unique=True)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=2, choices=GenderChoice.choices, default=GenderChoice.UNSET)
    address = models.CharField(max_length=60, null=True, blank=True)
    phone = models.CharField(max_length=15, validators=[phone_validator], blank=True)
    email = models.EmailField(_('email address'), unique=True, max_length=30, blank=True, null=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.ForeignKey(States, on_delete=models.CASCADE, null=True, blank=True)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    date_joined = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateField(blank=True, null=True)
    newsletter = models.CharField(
        max_length=5,
        choices=NewsChoice.choices,
        default=NewsChoice.FALSE,
        null=True, blank=True
    )
    avatar = models.ImageField(
        upload_to=get_profile_upload_path,
        null=True, blank=True,
        width_field='imagewidth',
        height_field='imageheight',
    )
    imagewidth = models.PositiveIntegerField(editable=False, default=65)
    imageheight = models.PositiveIntegerField(editable=False, default=65)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []


    def save(self, *args, **kwargs):
        if self.pk:
            try:
                existing_user = User.objects.get(pk=self.pk)
                if existing_user.avatar != self.avatar and existing_user.avatar:
                    existing_user.avatar.delete(save=False)
            except User.DoesNotExist:
                pass
        
        super(User, self).save(*args, **kwargs)
    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username if self.username else self.email



class ProductCategory(models.Model):
    slug = models.SlugField(allow_unicode=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to=get_category_upload_path,
        width_field='imagewidth',
        height_field='imageheight',
    )
    imagewidth = models.PositiveIntegerField(editable=False, default=401)
    imageheight = models.PositiveIntegerField(editable=False, default=401)

    class Meta:
        db_table = 'product_categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name



class Brand(models.Model):
    slug = models.SlugField(allow_unicode=True)
    name = models.CharField(max_length=50)
    logo = models.ImageField(
        upload_to=get_brand_logo_upload_path,
        null=True, blank=True,
        width_field='imagewidth',
        height_field='imageheight',
    )
    imagewidth = models.PositiveIntegerField(editable=False, default=50)
    imageheight = models.PositiveIntegerField(editable=False, default=50)

    def save(self, *args, **kwargs):
        try:
            this = Brand.objects.get(id=self.id)
            if this.logo != self.logo:
                this.logo.delete(save=False)
        except Brand.DoesNotExist:
            pass
        super(Brand, self).save(*args, **kwargs)

    class Meta:
        db_table = 'brand'
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self):
        return self.name



class ProductSize(models.Model):
    sizeno = models.CharField(max_length=20, help_text='Enter a product size')

    class Meta:
        db_table = 'product_size'
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'

    def __str__(self):
        return self.sizeno



class Color(models.Model):
    name = models.CharField(max_length=20, help_text="Enter a Product Color")
    hex_code = models.CharField(max_length=7, help_text="Enter a hex code for the color")

    class Meta:
        db_table = 'product_colors'
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'

    def __str__(self):
        return self.name



class Materials(models.Model):
    name = models.CharField(max_length=20, help_text="Enter a Product Material")

    class Meta:
        db_table = 'product_materials'
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'

    def __str__(self):
        return self.name



class Product(models.Model):
    slug = models.SlugField(allow_unicode=True)
    name = models.CharField(max_length=150)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    size = models.ManyToManyField(ProductSize, help_text="Enter Size of the product")
    mini_description = models.CharField(max_length=200)
    color = models.ManyToManyField(Color, help_text="Select Color of the product")
    material = models.ManyToManyField(Materials, help_text="Select Material of the Product")
    pic0 = models.ImageField(
        upload_to=get_product_upload_path,
        default='no-image.jpg',
        width_field='imagewidth',
        height_field='imageheight',
    )
    pic1 = models.ImageField(
        upload_to=get_product_upload_path,
        default='no-image.jpg',
        null=True, blank=True,
    )
    pic2 = models.ImageField(
        upload_to=get_product_upload_path,
        default='no-image.jpg',
        null=True, blank=True,
    )
    pic3 = models.ImageField(
        upload_to=get_product_upload_path,
        default='no-image.jpg',
        null=True, blank=True,
    )
    pic4 = models.ImageField(
        upload_to=get_product_upload_path,
        default='no-image.jpg',
        null=True, blank=True,
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        help_text="Category",
    )
    description = models.TextField(null=True, blank=True)
    imagewidth = models.PositiveIntegerField(editable=False, default=401)
    imageheight = models.PositiveIntegerField(editable=False, default=401)
    tags = models.ManyToManyField('Tag', related_name='products', blank=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def save(self, *args, **kwargs):
        if not self.id:  # if this is a new item
            newslug = f'{self.brand} {self.name}'
            self.slug = slugify(unidecode(newslug))
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name



class ProductInstance(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='instances')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    price = models.BigIntegerField(verbose_name='Price')
    off = models.IntegerField(default=0)
    instock = models.IntegerField()

    class Meta:
        db_table = 'product_instances'
        verbose_name = 'Product Instance'
        verbose_name_plural = 'Product Instances'

    def __str__(self):
        return f"{self.id} : {self.seller}"

    def new_price(self):
        return self.price - self.off if self.off else self.price



class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return f"{self.user} : {self.product}"



class Compare(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Compares"

    def __str__(self):
        return f"{self.user} : {self.product}"



class Tag(models.Model):
    name = models.CharField(max_length=100, help_text="Enter a tag name")

    class Meta:
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name



class Post(models.Model):
    title = models.CharField(max_length=100, help_text="Enter title for Post")
    slug = models.SlugField(max_length=255, unique=True, null=True)
    tags = models.ManyToManyField(Tag, help_text="Select tags for Post", related_name='posts')
    body = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True, null=True)
    pic = models.ImageField(
        upload_to=get_post_upload_path,
        null=True, blank=True, default='no-image.jpg',
        width_field='imagewidth',
        height_field='imageheight',
    )
    imagewidth = models.PositiveIntegerField(editable=False, default=401, null=True, blank=True)
    imageheight = models.PositiveIntegerField(editable=False, default=401, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='posts')

    class Meta:
        db_table = 'posts'
        verbose_name = 'Post'
        verbose_name_plural = "Posts"
        ordering = ['-published_date']

    @property
    def short_description(self):
        return truncatechars(self.body, 250)

    def save(self, *args, **kwargs):
        try:
            this = Post.objects.get(id=self.id)
            if this.pic != self.pic:
                this.pic.delete(save=False)
        except Post.DoesNotExist:
            pass
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    body = models.TextField()
    rating = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'review'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'


class Comments(models.Model):
    class StatusChoice(models.TextChoices):
        OK = 'T', "It's Ok"
        WAITING = 'W', "Waiting"

    writer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    body = models.CharField(max_length=500)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
    status = models.CharField(max_length=1, choices=StatusChoice.choices, default=StatusChoice.WAITING)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Comments"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.writer} : {self.body}"



class Coupon(models.Model):
    code = models.CharField(max_length=20)
    count = models.IntegerField()
    off = models.IntegerField(default=0, help_text="Off-price")
    expire = models.DateTimeField(verbose_name='Expire Date')

    class Meta:
        verbose_name_plural = "Coupons"

    def is_expired(self):
        return self.expire < timezone.now()

    def __str__(self):
        return f"Code: {self.code} - Count: {self.count}"


class Cart(models.Model):
    class SendChoice(models.TextChoices):
        IS_PAYED = 'T', 'Payed'
        IS_NOT_PAYED = 'F', 'Not Payed'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    product = models.ForeignKey(Product, verbose_name="Products", on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name="carts")
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, related_name="carts")
    material = models.ForeignKey(Materials, on_delete=models.CASCADE, related_name="carts")
    seller = models.ForeignKey(ProductInstance, on_delete=models.CASCADE, related_name="carts", null=True)
    count = models.IntegerField(default=1)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)
    payed = models.CharField(max_length=1, choices=SendChoice.choices, default=SendChoice.IS_NOT_PAYED)

    class Meta:
        verbose_name_plural = "Carts"

    def total(self):
        return self.seller.price * self.count

    def total_price(self):
        return self.total() - self.seller.off if self.seller.off else self.total()

    def final_price(self):
        return self.total_price() - self.coupon.off if self.coupon else self.total_price()

    def __str__(self):
        return f"Product: {self.product} - Seller: {self.seller} - User: {self.user}"


def get_sold_followup_code():
    return f'{random.randint(10, 99)}{strftime("%Y%m%d%H%M%S", gmtime())}'



class Sold(models.Model):
    SEND_CHOICES = {
        ('T', 'Package sent'),
        ('F', 'Package Wait for send'),
        ('B', 'Back to Store'),
    }
    follow_up_code = models.CharField(default=get_sold_followup_code, max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Buyer')
    products = models.ManyToManyField(Cart, verbose_name='Products')
    company = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=500)
    zip_code = models.CharField(max_length=10, verbose_name='Zip Code')
    state = models.ForeignKey(States, on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    total_price = models.BigIntegerField(help_text='Total Price With offers & Coupons')
    send_price = models.IntegerField()
    tax = models.IntegerField()
    total = models.BigIntegerField(help_text='Total Price With offers, Coupons, tax & send price.')
    desc = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now=True)
    sent = models.CharField(help_text='Is package sent?', default='F', verbose_name='Send Status', choices=SEND_CHOICES, max_length=1)

    def followup(self):
        return f'{random.randint(10000, 99999)}{self.id}'

    def __str__(self):
        return f"Order {self.follow_up_code} - Buyer: {self.user.email}"

    class Meta:
        verbose_name_plural = "Sold Products"


class ContactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Contact-us Table"

    def __str__(self):
        return f"{self.name}, {self.email}"


class CarouselBanner(models.Model):
    title = models.CharField(max_length=100, help_text="Enter a title for the carousel banner")
    subtitle = models.CharField(max_length=100, blank=True, null=True, help_text="Enter a subtitle for the carousel banner")
    description = models.TextField(max_length=280, help_text="Enter a description for the carousel banner")
    image = models.ImageField(
        upload_to=get_carousel_banner_upload_path,
    )
    imagewidth = models.PositiveIntegerField(editable=False, default=401, null=True, blank=True, help_text="Image width")
    imageheight = models.PositiveIntegerField(editable=False, default=401, null=True, blank=True, help_text="Image height")
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, blank=True, help_text="Select a category for the carousel banner", related_name='carousel_banners')

    def save(self, *args, **kwargs):
        try:
            this = CarouselBanner.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete(save=False)
        except CarouselBanner.DoesNotExist:
            pass
        super(CarouselBanner, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'carousel_banners'
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['-id']
