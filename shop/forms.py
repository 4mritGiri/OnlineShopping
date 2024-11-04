from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User , States, CarouselBanner
from django.core.validators import validate_email
from django.utils.text import slugify


"""class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(
        widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['email' , 'password' ]

    
    def clean_email(self): 
        email = self.cleaned_data['email']
        validate_email(email)
        user = User.objects.filter(email = email).exists()

        if user:
            raise ValidationError(_('Your email is already exists. Please try another one'))
        else:
            return email

    def clean_comfirmpwd(self):
        cleaned_data = super().clean_comfirmpwd()
        passwd = self.cleaned_data['password']
        passwd2 = self.cleaned_data['password2']

        if passwd is not None and passwd != passwd2:
            self.add_error("passwd2",'Passwords do not match')
      
        return cleaned_data

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.set_password = self.cleaned_data['password']

        if commit:
            # User is inactive on registration
            user.is_active = False
            user.save()

        return user
"""
    

class CarouselBannerForm(ModelForm):
    class Meta:
        model = CarouselBanner
        fields = ['title', 'description', 'image', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        
    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 20:
            raise ValidationError(_('Title must be less than 20 characters'))
        return title

    def clean_description(self):
        description = self.cleaned_data['description']
        if len(description) > 280:
            raise ValidationError(_('Description must be less than 280 characters'))
        return description
    
    def clean_image(self):
        image = self.cleaned_data['image']
        if image:
            if image.size > 10 * 1024 * 1024:
                raise ValidationError(_('Image file size must be less than 10 MB'))
            return image
        return None
    
    def clean_category(self):
        category = self.cleaned_data['category']
        if not category:
            raise ValidationError(_('Category is required'))
        return category
    
    def save(self, commit=True):
        carousel_banner = super().save(commit=False)
        carousel_banner.slug = slugify(carousel_banner.title)
        if commit:
            carousel_banner.save()
        return carousel_banner
    

class ProfileForm(ModelForm):
    NEWSLETTER_CHOICES = {
        ('TRUE', 'Subscribe to the newsletter'),
        ('FALSE', 'Not Subscribe to the newsletter'),
    }
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name' ,'email' , 'phone','username','address','newsletter','postcode' , 'city' , 'state', 'avatar' ]
        widgets = { 
            'avatar':forms.FileInput(
                attrs={'class':'form-control',
                'id':'input-avatar',
                'placeholder':"Avatar"}),
            
            'username':forms.TextInput(
                attrs={'class':'form-control',
                'id':'input-username', 
                'placeholder':"Username"}),
        
            'newsletter':forms.Select(
                attrs={'class':"form-control", 
                'id':"input-newsletter"}),

            'postcode' :forms.TextInput(
                attrs={'input_type':"number", 
                'class':"form-control", 'id':"input-postcode", 
                'placeholder':"Postal Code",}),

            'phone' :forms.TextInput(
                attrs={'class' : 'form-control', 
                'id' : 'input-phone', 
                'placeholder' : 'Phone Number'}),

            'first_name':forms.TextInput(
                attrs={'class':'form-control', 
                'id':'input-first-name', 
                'placeholder':"First Name"}),

            'last_name':forms.TextInput(
                attrs={'class':'form-control' , 
                'id':'input-last-name', 
                'placeholder':"Last Name"}),

            'email':forms.TextInput(
                attrs={'input_type':"email", 
                'class':'form-control' , 
                'id':'input-email', 
                'placeholder':"Email"}),

            'address':forms.TextInput(
                attrs={'class':'form-control' , 
                'id':'input-address',  
                'placeholder':"Address"}),

            'city':forms.TextInput(
                attrs={'class':'form-control' , 
                'id':'input-city',
                'placeholder':"City"}),

            'state':forms.Select(
                attrs={'class':'form-control' , 
                'id':'input-state',
                'placeholder':"State"}),
        }



class CheckoutForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['state'].choices = self.get_state_choices()

    def get_state_choices(self):
        return [(state.id, state.name) for state in States.objects.all()]

    company = forms.CharField(
        required=False, max_length=200, label='Company',
        widget=forms.TextInput(attrs={'class': "form-control", 'id': "input-payment-company", 'placeholder': "Company", 'name': "company"})
    )
    address = forms.CharField(
        max_length=500, label='Address',
        widget=forms.TextInput(attrs={'class': "form-control", 'id': "input-address", 'placeholder': "Address", 'name': "address"})
    )
    postcode = forms.CharField(
        max_length=10, label='Postal Code',
        widget=forms.TextInput(attrs={'class': "form-control", 'id': "input-post-code", 'placeholder': "Postal Code", 'name': "postcode"})
    )
    city = forms.CharField(
        max_length=50, label='City',
        widget=forms.TextInput(attrs={'class': "form-control", 'id': "input-city", 'placeholder': "City", 'name': "city"})
    )
    state = forms.ChoiceField(
        label='State',
        widget=forms.Select(attrs={'class': "form-control", 'id': "input-state", 'placeholder': "State", 'name': 'state'})
    )
    desc = forms.CharField(
        required=False, label='Description',
        widget=forms.Textarea(attrs={'rows': "4", 'class': "form-control", 'id': "confirm_comment", 'name': "desc"})
    )

    def clean_postcode(self):
        data = self.cleaned_data['postcode']
        if not data.isdigit():
            raise ValidationError(_('Postal Code must be only numbers.'))
        elif len(data) != 5:
            raise ValidationError(_('Postal Code must be 5 digits.'))
        return data



class PriceFilter(forms.Form):
    minPrice = forms.IntegerField(
        required=False, label='From',
        widget=forms.TextInput(attrs={'type': 'number', 'value': '0'})
    )
    maxPrice = forms.IntegerField(
        required=False, label='To',
        widget=forms.TextInput(attrs={'type': 'number', 'value': '0'})
    )

    def clean_minPrice(self):
        dataMin = self.cleaned_data['minPrice']
        dataMax = self.cleaned_data['maxPrice']
        if dataMin > dataMax:
            raise ValidationError(_("Invalid value! Please check again."))
        return dataMin

    def clean_maxPrice(self):
        dataMin = self.cleaned_data['minPrice']
        dataMax = self.cleaned_data['maxPrice']
        if dataMax < dataMin:
            raise ValidationError(_("Invalid value! Please check again."))
        return dataMax

# ist not complete and usable price filter 

