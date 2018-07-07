import factory
import datetime

from .models import User, Consumption

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n)

class ConsumptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Consumption
    datetime = datetime.datetime.strptime('2016-07-15+0900', '%Y-%m-%d%z')
    consumption = 300
