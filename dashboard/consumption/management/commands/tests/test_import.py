import pytest
from django.core.management import call_command
from consumption.models import User, Consumption, ConsumptionDetails


@pytest.mark.django_db
class TestCommand:
    def test_handle(self):
        # 事前にデータがないことを確認
        assert User.objects.count() == 0
        assert Consumption.objects.count() == 0
        assert ConsumptionDetails.objects.count() == 0

        call_command("import")

        assert User.objects.count() > 0
        assert Consumption.objects.count() > 0
        assert ConsumptionDetails.objects.count() > 0

        user = User.objects.get(id=3000)
        assert user.area == "a1"
        assert user.tariff == "t2"

        consumption = Consumption.objects.get(
            user_id=3000, datetime="2016-07-15 00:00:00+00:00"
        )
        assert consumption.amount == 39.0

        consumption_detail = ConsumptionDetails.objects.get(
            user_id=3000, date="2016-07-15"
        )
        assert consumption_detail.total == 14339.0
