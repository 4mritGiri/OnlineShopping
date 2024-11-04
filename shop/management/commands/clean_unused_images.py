import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps

class Command(BaseCommand):
   help = 'Delete unused images from media files'

   def handle(self, *args, **kwargs):
      media_root = settings.MEDIA_ROOT
      all_images = set()

      # List of models to check for image fields
      models_to_check = [
         'shop.User',
         'shop.ProductCategory',
         'shop.Brand',
         'shop.Product',
         'shop.Post',
         'shop.CarouselBanner',
      ]

      # Possible image field names
      image_field_names = ['image', 'avatar', 'logo', 'pic', 'pic0', 'pic1', 'pic2', 'pic3', 'pic4']

      # Collect all images referenced in the specified models
      for model_name in models_to_check:
         model = apps.get_model(model_name)
         for obj in model.objects.all():
               for field_name in image_field_names:
                  if hasattr(obj, field_name) and getattr(obj, field_name):
                     all_images.add(os.path.basename(getattr(obj, field_name).name))

      # Walk through the media directory
      for dirpath, dirnames, filenames in os.walk(media_root):
         for filename in filenames:
               if filename not in all_images:
                  file_path = os.path.join(dirpath, filename)
                  os.remove(file_path)  # Remove the file
                  self.stdout.write(self.style.SUCCESS(f'Removed unused image: {filename}'))

      self.stdout.write(self.style.SUCCESS('Cleanup complete.'))
