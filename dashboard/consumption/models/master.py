from django.db import models

from .base import TimestampedModel


class Area(TimestampedModel):
    area_name = models.CharField(max_length=30, unique=True)
    _area_dict = None

    @classmethod
    def get_area_dict(cls):
        if cls._area_dict is None:
            cls._area_dict = {area.area_name: area for area in cls.objects.all()}
        return cls._area_dict


class TariffPlan(TimestampedModel):
    plan_name = models.CharField(max_length=30, unique=True)
    _tariff_plan_dict = None

    @classmethod
    def get_tariff_plan_dict(cls):
        if cls._tariff_plan_dict is None:
            cls._tariff_plan_dict = {tariff_plan.plan_name: tariff_plan for tariff_plan in cls.objects.all()}
        return cls._tariff_plan_dict
