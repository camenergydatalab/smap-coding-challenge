import pytest
from consumption.models import User, Consumption, ConsumptionDetails


@pytest.fixture
def create_data():
    user1 = User.objects.create(id=1, area="a1", tariff="t1")
    user2 = User.objects.create(id=2, area="a2", tariff="t2")
    Consumption.objects.create(
        user=user1, datetime="2020-01-01 00:00:00+00:00", amount=10.0
    )
    Consumption.objects.create(
        user=user1, datetime="2020-01-01 01:00:00+00:00", amount=20.0
    )
    Consumption.objects.create(
        user=user2, datetime="2020-01-01 00:00:00+00:00", amount=30.0
    )
    Consumption.objects.create(
        user=user2, datetime="2020-01-01 01:00:00+00:00", amount=40.0
    )
    ConsumptionDetails.objects.create(user=user1, date="2020-01-01", total=30.0)
    ConsumptionDetails.objects.create(user=user2, date="2020-01-01", total=70.0)


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self, create_data):
        assert User.objects.count() == 2
        user1 = User.objects.get(id=1)
        assert user1.area == "a1"
        assert user1.tariff == "t1"
        user2 = User.objects.get(id=2)
        assert user2.area == "a2"
        assert user2.tariff == "t2"


@pytest.mark.django_db
class TestConsumptionModel:
    def test_create_consumption(self, create_data):
        assert Consumption.objects.count() == 4
        consumption1 = Consumption.objects.get(
            user_id=1, datetime="2020-01-01 00:00:00+00:00"
        )
        assert consumption1.amount == 10.0
        consumption2 = Consumption.objects.get(
            user_id=1, datetime="2020-01-01 01:00:00+00:00"
        )
        assert consumption2.amount == 20.0
        consumption3 = Consumption.objects.get(
            user_id=2, datetime="2020-01-01 00:00:00+00:00"
        )
        assert consumption3.amount == 30.0
        consumption4 = Consumption.objects.get(
            user_id=2, datetime="2020-01-01 01:00:00+00:00"
        )
        assert consumption4.amount == 40.0
        user1 = User.objects.get(id=1)
        assert user1.consumption_set.count() == 2
        assert user1.consumption_set.first() == consumption1
        assert user1.consumption_set.last() == consumption2
        user2 = User.objects.get(id=2)
        assert user2.consumption_set.count() == 2
        assert user2.consumption_set.first() == consumption3
        assert user2.consumption_set.last() == consumption4


@pytest.mark.django_db
class TestConsumptionDetailsModel:
    def test_create_consumption_details(self, create_data):
        assert ConsumptionDetails.objects.count() == 2
        consumption_detail1 = ConsumptionDetails.objects.get(
            user_id=1, date="2020-01-01"
        )
        assert consumption_detail1.total == 30.0
        consumption_detail2 = ConsumptionDetails.objects.get(
            user_id=2, date="2020-01-01"
        )
        assert consumption_detail2.total == 70.0
        user1 = User.objects.get(id=1)
        assert user1.consumptiondetails_set.count() == 1
        assert user1.consumptiondetails_set.first() == consumption_detail1
        user2 = User.objects.get(id=2)
        assert user2.consumptiondetails_set.count() == 1
        assert user2.consumptiondetails_set.first() == consumption_detail2
