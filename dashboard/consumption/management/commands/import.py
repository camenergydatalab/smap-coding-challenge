from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'import data'

    def handle(self, *args, **options):
        print("Implement me!")
