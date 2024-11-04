import os
import requests
from django.core.files import File
from django.core.management.base import BaseCommand
from faker import Faker
import random
from shop.models import User, Product, ProductCategory, Brand, States, ProductSize, Materials, Color, ProductInstance

class Command(BaseCommand):
   help = 'Generate fake data for testing'

   def handle(self, *args, **kwargs):
      fake = Faker()

      # Generate fake users with avatars
      for _ in range(5):
         # Download a random avatar image
         image_url = 'https://picsum.photos/400/400?random'
         response = requests.get(image_url)

         if response.status_code == 200:
               # Save the image to a temporary file
               image_path = f'/tmp/{fake.slug()}.jpg'
               with open(image_path, 'wb') as f:
                  f.write(response.content)

               # Create the user
               user = User.objects.create(
                  email=fake.email(),
                  username=fake.user_name(),
                  password="FakePassword",
                  phone=fake.phone_number(),
                  address=fake.address(),
                  city=fake.city(),
                  state=States.objects.order_by('?').first(),
                  postcode=fake.postcode(),
                  description=fake.text(max_nb_chars=100),
                  first_name=fake.first_name(),
                  last_name=fake.last_name(),
                  is_staff=fake.boolean(),
                  is_active=fake.boolean(),
               )

               # Attach the avatar to the user
               with open(image_path, 'rb') as f:
                  user.avatar.save(f'{user.username}.jpg', File(f), save=True)

               # Clean up the temporary file
               os.remove(image_path)

               self.stdout.write(self.style.SUCCESS(f'Successfully generated user: {user.username}'))
         else:
               self.stdout.write(self.style.WARNING('Failed to download avatar, skipping user creation'))

      # Generate fake product categories with images
      for _ in range(5):
         # Download a random category image
         image_url = 'https://picsum.photos/400/400?random'
         response = requests.get(image_url)

         if response.status_code == 200:
               # Save the image to a temporary file
               image_path = f'/tmp/{fake.slug()}.jpg'
               with open(image_path, 'wb') as f:
                  f.write(response.content)

               # Create the product category
               product_category = ProductCategory.objects.create(
                  name=fake.word(),
                  slug=fake.slug(),
               )

               # Attach the image to the product category
               with open(image_path, 'rb') as f:
                  product_category.image.save(f'{product_category.slug}.jpg', File(f), save=True)

               # Clean up the temporary file
               os.remove(image_path)

               self.stdout.write(self.style.SUCCESS(f'Successfully generated product category: {product_category.name}'))
         else:
               self.stdout.write(self.style.WARNING('Failed to download image, skipping product category creation'))

      # Generate fake brands with logos
      for _ in range(5):
         # Download a random brand logo
         image_url = 'https://picsum.photos/400/400?random'
         response = requests.get(image_url)

         if response.status_code == 200:
               # Save the image to a temporary file
               image_path = f'/tmp/{fake.slug()}.jpg'
               with open(image_path, 'wb') as f:
                  f.write(response.content)

               # Create the brand
               brand = Brand.objects.create(
                  name=fake.company(),
                  slug=fake.slug(),
               )

               # Attach the logo to the brand
               with open(image_path, 'rb') as f:
                  brand.logo.save(f'{brand.slug}.jpg', File(f), save=True)

               # Clean up the temporary file
               os.remove(image_path)

               self.stdout.write(self.style.SUCCESS(f'Successfully generated brand: {brand.name}'))
         else:
               self.stdout.write(self.style.WARNING('Failed to download logo, skipping brand creation'))

      # Generate fake materials
      materials = []
      for _ in range(5):
         material = Materials.objects.create(
               name=fake.word(),
         )
         materials.append(material)

      # Generate fake colors
      colors = []
      for _ in range(5):
         color = Color.objects.create(
               name=fake.word(),
               hex_code=fake.hex_color(),
         )
         colors.append(color)

      # Generate fake sizes
      sizes = []
      for _ in range(5):
         size = ProductSize.objects.create(
               sizeno=f"{fake.random_int(min=1, max=40)} X {fake.random_int(min=1, max=50)}",
         )
         sizes.append(size)

      # Generate fake products with images
      for _ in range(20):
         # Download a random furniture image
         image_url = 'https://picsum.photos/400/400?random'
         response = requests.get(image_url)

         if response.status_code == 200:
               # Save the image to a temporary file
               image_path = f'/tmp/{fake.slug()}.jpg'
               with open(image_path, 'wb') as f:
                  f.write(response.content)

               # Create the product
               product = Product.objects.create(
                  name=fake.word(),
                  slug=fake.slug(),
                  brand=Brand.objects.order_by('?').first(),
                  category=ProductCategory.objects.order_by('?').first(),
                  mini_description=fake.text(max_nb_chars=100),
               )
               product.size.set(random.sample(sizes, random.randint(1, 3)))
               product.material.set(random.sample(materials, random.randint(1, 3)))
               product.color.set(random.sample(colors, random.randint(1, 5)))

               # Attach the image to the product
               with open(image_path, 'rb') as f:
                  product.pic0.save(f'{product.slug}.jpg', File(f), save=True)
                  product.pic1.save(f'{product.slug}.jpg', File(f), save=True)
                  product.pic2.save(f'{product.slug}.jpg', File(f), save=True)
                  product.pic3.save(f'{product.slug}.jpg', File(f), save=True)

               # Clean up the temporary file
               os.remove(image_path)

               self.stdout.write(self.style.SUCCESS(f'Successfully generated product: {product.name}'))
         else:
               self.stdout.write(self.style.WARNING('Failed to download image, skipping product creation'))

      # Product Instances
      for _ in range(20):
         product_instance = ProductInstance.objects.create(
               product=Product.objects.order_by('?').first(),
               seller=User.objects.order_by('?').first(),
               price=fake.random_int(min=500, max=99999),
               off=fake.random_int(min=0, max=50),
               instock=fake.random_int(min=0, max=100),
         )

      self.stdout.write(self.style.SUCCESS('Finished generating fake data with images'))
