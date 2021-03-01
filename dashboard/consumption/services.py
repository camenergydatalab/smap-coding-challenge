# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.db.models import Avg, Sum

from .models import Consumption, User


def create_chart_data():
    """create chart data

    Create data for chart

    Returns: dict:
        {
            'labels': list[str], ...datetime labels for data,
            'total_data': list[str], ...total consumption data,
            'avg_data': list[str] ...average consumption dat
        }
    Raises:
        Consumption.DoesNotExist: if Consumption is not found
    """
    labels = []
    total_data = []
    avg_data = []

    # aggregate consumption data
    consum_data = Consumption.objects.values('datetime').annotate(
        Avg('consumption'), Sum('consumption')).order_by('datetime')

    if consum_data.exists():
        for consum in consum_data:
            labels.append(consum['datetime'].strftime("%Y-%m-%d %H:%M:%S"))
            total_data.append(str(consum['consumption__sum']))
            avg_data.append(str(consum['consumption__avg']))
    else:
        raise Consumption.DoesNotExist

    return {
        'labels': labels,
        'total_data': total_data,
        'avg_data': avg_data
    }


def create_table_data():
    """create table data

    Create data for table

    Returns: dict:
        {
            'data': [{
                'id': int, ...user id
                'area': str, ...user area,
                'tariff': str, ...user tariff,
                'average': str, ...user's average consumption
            }],
            'min_value': int, ... minimum use's average consumption
            'max_value': int, ... maximum use's average consumption
        }

    Raises:
        User.DoesNotExist: if user is not found
    """
    data = []
    avg_consum_data = get_user_avg_consum()

    user_data = User.objects.all()
    if user_data.exists():
        for user in user_data:
            data.append({
                'id': user.id,
                'area': user.area,
                'tariff': user.tariff,
                'average': avg_consum_data[user.id]
            })
    else:
        raise User.DoesNotExist

    min_value = min(data, key=lambda x: Decimal(x['average']))['average']
    max_value = max(data, key=lambda x: Decimal(x['average']))['average']

    return {
        'data': data,
        'min_value': str(min_value),
        'max_value': str(max_value),
    }


def get_user_avg_consum():
    """get user's average consumption

    Get user's average comsumption

    Returns: dict:
        {
            int (user id): str ...average consumption
        }

    Raises:
        Consumption.DoesNotExist: if Consumption is not found
    """
    avg_consum_data = {}

    consum_data = Consumption.objects.values('user_id').annotate(
        Avg('consumption'))
    if consum_data.exists():
        for data in consum_data:
            avg_consum_data[data['user_id']] = str(data['consumption__avg'])
    else:
        raise Consumption.DoesNotExist

    return avg_consum_data


def create_user_chart_data(user):
    """get user's average consumption

    Get user's average comsumption

    Args:
        user (User object): user model object

    Returns: dict:
        {
            'labels': list[str], ...datetime labels for data,
            'data': list[str], ...user's consumption data
        }

    Raises:
        User.DoesNotExist: if user is not found
    """
    labels = []
    data = []

    # aggregate consumption data
    consum_data = Consumption.objects.filter(user_id=user).order_by('datetime')
    if consum_data.exists():
        for consum in consum_data:
            labels.append(consum.datetime.strftime("%Y-%m-%d %H:%M:%S"))
            data.append(str(consum.consumption))
    else:
        raise User.DoesNotExist

    return {
        'labels': labels,
        'data': data,
    }
