# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from .queries import ConsumptionQueryset, UserQueryset


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
    consum_data = ConsumptionQueryset.get_consumption_avg_and_sum()
    for consum in consum_data:
        labels.append(consum['datetime'].strftime("%Y-%m-%d %H:%M:%S"))
        total_data.append(str(consum['consumption__sum']))
        avg_data.append(str(consum['consumption__avg']))

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
    consum_data = get_user_avg_consum()

    user_data = UserQueryset.get_all_user()
    for user in user_data:
        data.append({
            'id': user.id,
            'area': user.area,
            'tariff': user.tariff,
            'average': consum_data[user.id]
        })

    min_value = min(data, key=lambda x: Decimal(x['average']))['average']
    max_value = max(data, key=lambda x: Decimal(x['average']))['average']

    return {
        'data': data,
        'min_value': str(min_value),
        'max_value': str(max_value),
    }


def get_user_avg_consum():
    """get user's average consumption

    Get user's average comsumption as dict

    Returns: dict:
        {
            int (user id): str ...average consumption
        }
    """
    avg_consum_data = {}

    consum_data = ConsumptionQueryset.get_each_user_average_consumption()
    for data in consum_data:
        avg_consum_data[data['user_id']] = str(data['consumption__avg'])

    return avg_consum_data


def create_user_chart_data(user_id):
    """create user chart data

    Create chart data for specified user

    Args:
        user_id (int): user id

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
    consum_data = ConsumptionQueryset.get_user_consumption_order_by_date(
        user_id)
    for consum in consum_data:
        labels.append(consum.datetime.strftime("%Y-%m-%d %H:%M:%S"))
        data.append(str(consum.consumption))

    return {
        'labels': labels,
        'data': data,
    }
