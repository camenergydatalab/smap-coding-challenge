from consumption.utils.time_utils import get_local_now_time
from django.db import models
from model_utils import Choices

from .base import TimestampedModel
from .master import Area, TariffPlan


class User(TimestampedModel):
    CONTINUING = "continuing"
    STOPPED = "stopped"
    WITHDRAWN = "withdrawn"

    USER_STATUS = Choices(
        (CONTINUING, "continuing"),
        (STOPPED, "stopped"),
        (WITHDRAWN, "withdrawn"),
    )

    user_id = models.CharField(max_length=20, unique=True)
    user_status = models.CharField(max_length=20, choices=USER_STATUS, default=CONTINUING)


class UserConsumptionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    measurement_at = models.DateTimeField()
    consumption_amount = models.DecimalField(max_digits=6, decimal_places=2)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "measurement_at"], name="user_consumption_history_unique"),
        ]


class UserContractHistory(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    tariff_plan = models.ForeignKey(TariffPlan, on_delete=models.CASCADE)
    contract_start_at = models.DateTimeField(default=get_local_now_time)
    contract_end_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "area", "tariff_plan"], name="user_contract_history_unique"),
        ]
