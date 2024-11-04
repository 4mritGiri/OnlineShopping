import csv
from django.core.management.base import BaseCommand
from shop.models import States

class Command(BaseCommand):
   help = 'Upload states from a CSV file'

   def add_arguments(self, parser):
      parser.add_argument('csv_file', type=str, help='The path to the CSV file containing the states')

   def handle(self, *args, **kwargs):
      csv_file_path = kwargs['csv_file']

      try:
         with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
               reader = csv.reader(csvfile)
               for row in reader:
                  state_name = row[0] 
                  state, created = States.objects.get_or_create(name=state_name)
                  if created:
                     self.stdout.write(self.style.SUCCESS(f'Successfully added state: {state_name}'))
                  else:
                     self.stdout.write(self.style.WARNING(f'State already exists: {state_name}'))
      except FileNotFoundError:
         self.stdout.write(self.style.ERROR(f'File not found: {csv_file_path}'))
      except Exception as e:
         self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
