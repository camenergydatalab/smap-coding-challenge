from django.core.management.base import BaseCommand

from consumption.import_csv import import_user, import_consumption

class Command(BaseCommand):
    help = 'import data'

    def add_arguments(self, parser):
        parser.add_argument('user_csv_path', type=str, help='Set user csv file path')
        parser.add_argument('consumption_csv_dir', type=str, help='Set consumption csv directory path')

    def handle(self, *args, **options):
        import_user(options['user_csv_path'])
        import_consumption(options['consumption_csv_dir'])
