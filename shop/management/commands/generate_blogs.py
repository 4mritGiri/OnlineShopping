import os
import requests
import random
from django.core.files import File
from django.core.management.base import BaseCommand
from faker import Faker
from shop.models import User, Post, Tag, Comments

class Command(BaseCommand):
   help = 'Generate fake blog posts for testing'

   def handle(self, *args, **kwargs):
      fake = Faker()

      # Generate 10 random tags
      for _ in range(10):
         Tag.objects.create(name=fake.word())
         
      # Generate fake blog posts with images
      for _ in range(10):
         # Download a random image for the post
         image_url = 'https://picsum.photos/400/400?random'
         response = requests.get(image_url)

         if response.status_code == 200:
            # Save the image to a temporary file
            image_path = f'/tmp/{fake.slug()}.jpg'
            with open(image_path, 'wb') as f:
               f.write(response.content)

            # Create the post
            post = Post.objects.create(
               title=fake.sentence(),
               slug=fake.slug(),
               body=fake.paragraph(nb_sentences=5),
               created_by=User.objects.order_by('?').first(),
            )

            # Attach the image to the post
            with open(image_path, 'rb') as f:
               post.pic.save(f'{post.slug}.jpg', File(f), save=True)

            # Clean up the temporary file
            os.remove(image_path)

            # Generate comments for the post
            for _ in range(random.randint(4, 8)):
               Comments.objects.create(
                  writer=User.objects.order_by('?').first(),
                  body=fake.paragraph(nb_sentences=1),
                  post=post,
                  status=Comments.StatusChoice.OK,
               )

            # Assign a random tag to the post
            random_tag = Tag.objects.order_by('?').first()
            if random_tag:
               post.tags.set([random_tag])

            self.stdout.write(self.style.SUCCESS(f'Successfully generated blog post: {post.title}'))
         else:
            self.stdout.write(self.style.WARNING('Failed to download image, skipping blog post creation'))

      self.stdout.write(self.style.SUCCESS('Finished generating fake blog posts with images'))
