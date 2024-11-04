import os
import requests
import random
from django.core.files import File
from django.core.management.base import BaseCommand
from faker import Faker
from shop.models import CarouselBanner, ProductCategory

class Command(BaseCommand):
   help = 'Generate fake Carousel Banner for testing'

   def handle(self, *args, **kwargs):
      fake = Faker()

      # Generate carousel banners
      for _ in range(random.randint(2, 8)):
         # Download a random image for the carousel banner 16:9
         image_url = 'https://picsum.photos/1600/900?random'
         response = requests.get(image_url)

         if response.status_code == 200:
            # Save the image to a temporary file
            image_path = f'/tmp/{fake.slug()}.jpg'
            with open(image_path, 'wb') as f:
               f.write(response.content)

            # Create the carousel banner
            carousel_banner = CarouselBanner.objects.create(
               title=fake.sentence(),
               subtitle=fake.sentence(),
               description=fake.paragraph(nb_sentences=1),
               category=ProductCategory.objects.order_by('?').first(),
            )

            # Attach the image to the carousel banner
            with open(image_path, 'rb') as f:
                  carousel_banner.image.save(f'{carousel_banner.title}.jpg', File(f), save=True)

            # Clean up the temporary file
            os.remove(image_path)

            self.stdout.write(self.style.SUCCESS(f'Successfully generated carousel banner: {carousel_banner.title}'))
         else:
            self.stdout.write(self.style.WARNING('Failed to download image, skipping carousel banner creation'))
