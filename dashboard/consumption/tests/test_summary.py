import datetime
from operator import attrgetter

from django.test import TestCase, RequestFactory
from django.utils.timezone import make_aware

from consumption.models import UserData, ConsumptionData
from consumption.views import SummaryView


def dt_from_unixtime(unixtime):
    dt = datetime.datetime.fromtimestamp(unixtime)
    return make_aware(dt)


class ContextDataTests(TestCase):
    @staticmethod
    def get_response(request, *args, **kwargs):
        view = SummaryView()
        view.request = request
        view.args = args
        view.kwargs = kwargs
        response = view.get(request, args, kwargs)
        return response

    def test_empty_user_data(self):
        """ユーザデータが未登録の場合"""
        request = RequestFactory().get("/summary/")
        response = self.get_response(request)
        context_data = response.context_data
        self.assertQuerysetEqual(context_data["users"], [])
        self.assertQuerysetEqual(context_data["aggregate_consumption"], [])

    def test_user_data(self):
        """ユーザデータが含まれること"""
        UserData.objects.create(id="1000", area="a1", tariff="t1")
        request = RequestFactory().get("/summary/")
        response = self.get_response(request)
        context_data = response.context_data
        self.assertQuerysetEqual(
            context_data["users"], [1000], transform=attrgetter("id")
        )
        self.assertQuerysetEqual(context_data["aggregate_consumption"], [])

    def test_user_data_pagination(self):
        """ページネーションテスト"""
        UserData.objects.bulk_create(
            [
                UserData(id=user_id, area="a1", tariff="t1")
                for user_id in range(1000, 1021)
            ]
        )
        request = RequestFactory().get("/summary/")
        response = self.get_response(request)
        context_data = response.context_data
        self.assertQuerysetEqual(
            context_data["users"], list(range(1000, 1020)), transform=attrgetter("id")
        )

        request = RequestFactory().get("/summary/", data={"page": "2"})
        response = self.get_response(request)
        context_data = response.context_data
        self.assertQuerysetEqual(
            context_data["users"], [1020], transform=attrgetter("id")
        )

    def test_aggregate_consumption(self):
        """日付ごとの消費量集計データが含まれること"""
        UserData.objects.create(id="1000", area="a1", tariff="t1")
        UserData.objects.create(id="1001", area="a1", tariff="t1")

        now_unixtime = datetime.datetime(2023, 1, 1, 0, 0, 0).timestamp()

        # 1日分のunixtime
        day_unixtime = 60 * 60 * 24

        # 1か月分のデータを作成 consumption 101 ~ 131
        create_data_num = 31
        ConsumptionData.objects.bulk_create(
            [
                ConsumptionData(
                    user_id="1000",
                    datetime=dt_from_unixtime(
                        now_unixtime + index * day_unixtime
                    ),  # １日ごとにインクリメントする
                    consumption=101 + index,
                )
                for index in range(create_data_num)
            ]
        )

        with self.subTest("1人分のユーザでデータ集計する"):
            request = RequestFactory().get("/summary/")
            response = self.get_response(request)
            context_data = response.context_data

            # total
            self.assertQuerysetEqual(
                context_data["aggregate_consumption"],
                [float(101 + index) for index in range(create_data_num)],
                transform=lambda s: s["total"],
            )

            # average
            self.assertQuerysetEqual(
                context_data["aggregate_consumption"],
                [float(101 + index) for index in range(create_data_num)],
                transform=lambda s: s["average"],
            )

        with self.subTest("2人目のユーザでデータ集計する"):
            # 別ユーザの1か月分のデータを作成 consumption 201 ~ 231
            ConsumptionData.objects.bulk_create(
                [
                    ConsumptionData(
                        user_id="1001",
                        datetime=dt_from_unixtime(now_unixtime + index * day_unixtime),
                        consumption=201 + index,
                    )
                    for index in range(create_data_num)
                ]
            )
            request = RequestFactory().get("/summary/")
            response = self.get_response(request)
            context_data = response.context_data

            # total
            self.assertQuerysetEqual(
                context_data["aggregate_consumption"],
                [float(302 + index * 2) for index in range(create_data_num)],
                transform=lambda s: s["total"],
            )

            # average
            self.assertQuerysetEqual(
                context_data["aggregate_consumption"],
                [float((302 + index * 2) / 2) for index in range(create_data_num)],
                transform=lambda s: s["average"],
            )


class TemplateTests(TestCase):
    @staticmethod
    def get_response(request, *args, **kwargs):
        view = SummaryView()
        view.request = request
        view.args = args
        view.kwargs = kwargs
        response = view.get(request, args, kwargs)
        return response

    def test_empty_user_data(self):
        """ユーザデータが未登録の場合"""
        request = RequestFactory().get("/summary/")
        response = self.get_response(request)
        response.render()
        self.assertInHTML("<td>no data</td>", str(response.content))

    def test_user_data(self):
        """ユーザデータがある場合"""
        UserData.objects.create(id="1000", area="a1", tariff="t1")

        request = RequestFactory().get("/summary/")
        response = self.get_response(request)
        response.render()

        self.assertInHTML(
            r"""<a href="/detail/1000/">\n 1000\n</a>""", str(response.content)
        )
        self.assertInHTML("<td>a1</td>", str(response.content))
        self.assertInHTML("<td>t1</td>", str(response.content))
