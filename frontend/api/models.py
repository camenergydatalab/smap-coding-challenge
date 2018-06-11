from django.db import models


class Consumer(models.Model):
    UNKNOWN = 'unknown'
    LOW_VOLTAGE = 'low'
    HIGH_VOLTAGE = 'high'
    EXTRA_HIGH_VOLTAGE = 'extra_high'

    CONSUMER_TYPE = (
        (UNKNOWN, 'Unknown'),
        (LOW_VOLTAGE, 'Low voltage'),
        (HIGH_VOLTAGE, 'High voltage'),
        (EXTRA_HIGH_VOLTAGE, 'Extra-high voltage'))

    CONSUMER_TYPE_MAP = {
        UNKNOWN: 'Unknown',
        LOW_VOLTAGE: 'Low voltage',
        HIGH_VOLTAGE: 'High voltage',
        EXTRA_HIGH_VOLTAGE: 'Extra-high voltage'
    }

    name = models.CharField(max_length=150)
    consumer_type = models.CharField(max_length=30, choices=CONSUMER_TYPE, default=UNKNOWN)


class MonthlyStatistics(models.Model):
    consumer = models.ForeignKey('Consumer', on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    consumption = models.FloatField(blank=True, null=True)
    total_bill = models.FloatField(blank=True, null=True)
    total_cost = models.FloatField(blank=True, null=True)
