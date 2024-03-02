from django.db import models
from .base import TimestampedModel


class Area(TimestampedModel):
    area_name = models.CharField(max_length=30, unique=True)
    _area_map = None

    @classmethod
    def get_area_map(cls):
        if cls._area_map is None:
            cls._area_map = {area.area_name: area for area in cls.objects.all()}
        return cls._area_map


class TariffPlan(TimestampedModel):
    plan_name = models.CharField(max_length=30, unique=True)
    _tariff_plan_map = None

    @classmethod
    def get_tariff_plan_map(cls):
        if cls._tariff_plan_map is None:
            cls._tariff_plan_map = {tariff_plan.plan_name: tariff_plan for tariff_plan in cls.objects.all()}
        return cls._tariff_plan_map
