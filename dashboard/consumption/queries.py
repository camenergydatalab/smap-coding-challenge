# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Avg, Sum

from .models import Consumption, User


class ConsumptionQueryset():
    """queryset for consumption data
    """
    def get_consumption_avg_and_sum():
        """get average and sum of consumption

        Get average and sum of consumption all time

        Returns:
            QuerySet (dict): consumption data for each user

        Raises:
            Consumption.DoesNotExist: if Consumption is not found
        """
        consum_data = Consumption.objects.values('datetime').annotate(
            Avg('consumption'), Sum('consumption')).order_by('datetime')
        if consum_data.exists():
            return consum_data
        else:
            raise Consumption.DoesNotExist

    def get_each_user_average_consumption():
        """get user's average consumption

        Get user's average comsumption

        Returns:
            QuerySet (dict): consumption data for each user

        Raises:
            Consumption.DoesNotExist: if Consumption is not found
        """
        consum_data = Consumption.objects.values('user_id').annotate(
            Avg('consumption'))
        if consum_data.exists():
            return consum_data
        else:
            raise Consumption.DoesNotExist

    def get_user_consumption_order_by_date(user_id):
        """get user's consumption data order by datetime

        Get specified user's comsumption.

        Args:
            user_id (int): user id

        Returns:
            QuerySet (Consumption): consumption data for each user

        Raises:
            Consumption.DoesNotExist: if user is not found
        """
        user = User.objects.get(id=user_id)
        consum_data = Consumption.objects.filter(
            user_id=user).order_by('datetime')
        if consum_data.exists():
            return consum_data
        else:
            raise Consumption.DoesNotExist


class UserQueryset():
    """queryset for user data
    """
    def get_all_user():
        """get all user

        Get All user data.

        Args:
            user (User object): user model object

        Returns:
            QuerySet (User): all user data

        Raises:
            User.DoesNotExist: if user is not found
        """
        user_data = User.objects.all()
        if user_data.exists():
            return user_data
        else:
            raise User.DoesNotExist
