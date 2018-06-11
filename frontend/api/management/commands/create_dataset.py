import random
from django.core.management.base import BaseCommand
from api.models import Consumer, MonthlyStatistics


class Command(BaseCommand):
    help = "Create dataset. Please do no run that command if you haven't drink SMAP coffee yet." 

    def handle(self, *args, **options):
        check = input(self.style.ERROR(
            "You should not run this command as database is already populated with necessary data. "
            "Are you SMAP staff? Do you want to recreate the dataset? If you answered yes both times, then type 'yes': "
        ))

        if check == 'yes':
            first_names = [
                'John', 'Tom', 'Mary', 'Tina', 'Anne', 'Joseph', 'Jim', 'Lily', 'Harry', 'Dianne',
                'Olivia', 'Rose', 'Megan', 'Julia', 'Adam', 'Alan', 'Brandon', 'Brian', 'Cameron',
                'Carl',  'Charles', 'Evan', 'Frank', 'Gavin'
            ]

            last_names = [
                'Arnold', 'Avery', 'Baker', 'Bell', 'Bond', 'Carr', 'Clark', 'Davis', 'Duncan', 'Glover',
                'Gibson', 'Hamilton', 'Hart', 'Jackson', 'Jones', 'Kerr', 'King', 'Miller', 'Nash', 'Nolan',
                'Oliver', 'Page', 'Piper', 'Rees', 'Short', 'Skinner', 'Taylor', 'Watson', 'Young', 'Martin',
                'May', 'Know', 'Lewis', 'Lee', 'Grey', 'Clinton', 'Dyer', 'Cameron', 'Butler', 'Walsh', 'Wallace'
            ]

            for i in range(0, 60):
                name = "{} {}".format(random.choice(first_names), random.choice(last_names))
                consumer_type = random.choice([Consumer.LOW_VOLTAGE, Consumer.HIGH_VOLTAGE, Consumer.EXTRA_HIGH_VOLTAGE])
                consumer = Consumer.objects.create(
                    name=name,
                    consumer_type=consumer_type
                )

                for year in [2016, 2017]:
                    for month in range(1, 13):
                        consumption = 10000 * (random.randrange(50, 99) / 100)
                        total_bill = consumption * (0.17 * (random.randrange(80, 99) / 100))
                        total_cost = consumption * (0.17 * (random.randrange(80, 99) / 100))
                        MonthlyStatistics.objects.create(
                            consumer=consumer,
                            year=year,
                            month=month,
                            consumption=consumption,
                            total_bill=total_bill,
                            total_cost=total_cost
                        )
                    self.stdout.write(self.style.SUCCESS("Consumer {} created.".format(i+1)))
