# -*- coding: utf-8 -*-
import pytest
from django.urls import reverse
from ..models import User, Consumption, ConsumptionDetails
from datetime import date, datetime


@pytest.fixture
def create_test_data():
    # テスト用のデータを作成
    user1 = User.objects.create(id=1)
    user2 = User.objects.create(id=2)
    Consumption.objects.create(
        user=user1, amount=100, datetime=datetime(2024, 1, 1, 0, 0, 0)
    )
    Consumption.objects.create(
        user=user2, amount=200, datetime=datetime(2024, 1, 2, 0, 0, 0)
    )
    ConsumptionDetails.objects.create(user=user1, date=date(2024, 1, 1), total=50)
    ConsumptionDetails.objects.create(user=user1, date=date(2024, 1, 2), total=60)
    ConsumptionDetails.objects.create(user=user2, date=date(2024, 1, 1), total=100)
    ConsumptionDetails.objects.create(user=user2, date=date(2024, 1, 2), total=120)


@pytest.mark.django_db
def test_summary_view(client, create_test_data):
    url = reverse("summary")
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["users"].count() == 2
    assert response.context["users"][0].total_consumption == 100
    assert response.context["users"][0].average_consumption == 100
    assert response.context["users"][1].total_consumption == 200
    assert response.context["users"][1].average_consumption == 200
    assert "日ごとのエネルギー総消費量" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_detail_view(client, create_test_data):
    user_id = User.objects.first().id
    url = reverse("detail") + f"?id={user_id}"
    response = client.get(url)
    assert response.status_code == 200
    assert int(response.context["user_id"]) == user_id
    assert len(response.context["monthly_data"]) == 1
    assert response.context["monthly_data"][0]["month"] == "2024-01"
    assert response.context["monthly_data"][0]["total_sum"] == 110
    assert "日ごとのエネルギー総消費量" in response.content.decode("utf-8")
