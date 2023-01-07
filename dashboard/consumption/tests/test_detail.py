import datetime
from operator import attrgetter

from django.http import Http404
from django.test import TestCase, RequestFactory
from django.utils.timezone import make_aware

from consumption.models import UserData, ConsumptionData
from consumption.views import UserDetailView

# 30分のunixtime
minute_30_unixtime = 60 * 30
# 1日分のunixtime
day_unixtime = 60 * 60 * 24
now_unixtime = datetime.datetime(2023, 1, 1, 0, 0, 0).timestamp()


def dt_from_unixtime(unixtime):
    dt = datetime.datetime.fromtimestamp(unixtime)
    return make_aware(dt)


class ContextDataTests(TestCase):
    @staticmethod
    def get_response(request, *args, **kwargs):
        view = UserDetailView()
        view.request = request
        view.args = args
        view.kwargs = kwargs
        response = view.get(request, args, kwargs)
        return response

    def test_no_exist_data(self):
        request = RequestFactory().get("/detail/1000/")
        with self.assertRaisesMessage(Http404, "No user data found matching the query"):
            self.get_response(request, user_id=1000)

    def test_user_data_and_no_consumption_data(self):
        UserData.objects.create(id="1000", area="a1", tariff="t1")
        request = RequestFactory().get("/detail/1000/")
        response = self.get_response(request, user_id=1000)
        context_data = response.context_data
        self.assertEqual(context_data["user"].pk, 1000)
        self.assertQuerysetEqual(context_data["consumption_list"], [])
        self.assertIsNone(context_data["current_date"])
        self.assertIsNone(context_data["prev_date"])
        self.assertIsNone(context_data["next_date"])

    def test_consumption_data_list(self):
        """ 同じ日付で複数の消費量データ """
        UserData.objects.create(id="1000", area="a1", tariff="t1")

        ConsumptionData.objects.bulk_create([
            ConsumptionData(
                user_id="1000",
                datetime=dt_from_unixtime(now_unixtime + index * minute_30_unixtime),
                consumption=100 + index
            ) for index in range(10)
        ])

        request = RequestFactory().get("/detail/1000/")
        response = self.get_response(request, user_id=1000)
        context_data = response.context_data
        self.assertEqual(context_data["user"].pk, 1000)
        self.assertQuerysetEqual(context_data["consumption_list"], [100 + index for index in range(10)],
                                 transform=attrgetter("consumption"))
        self.assertEqual(context_data["current_date"], "2023-01-01")
        self.assertIsNone(context_data["prev_date"])
        self.assertIsNone(context_data["next_date"])

    def test_per_date_consumption_data_list(self):
        """ 日付を指定してデータが表示されるかテスト """
        UserData.objects.create(id="1000", area="a1", tariff="t1")

        # 1日毎の消費量データを10日分作成する。
        ConsumptionData.objects.bulk_create([
            ConsumptionData(
                user_id="1000",
                datetime=dt_from_unixtime(now_unixtime + index * day_unixtime),
                consumption=100 + index
            ) for index in range(10)
        ])

        request = RequestFactory().get("/detail/1000/")
        response = self.get_response(request, user_id=1000)
        context_data = response.context_data
        self.assertEqual(context_data["user"].pk, 1000)

        with self.subTest("日付が指定されていない場合は最新日のデータが表示されること"):
            self.assertQuerysetEqual(context_data["consumption_list"], [109.0], transform=attrgetter("consumption"))
            self.assertEqual(context_data["current_date"], "2023-01-10")
            self.assertEqual(context_data["prev_date"], "2023-01-09")
            self.assertIsNone(context_data["next_date"])

        with self.subTest("日付を指定してデータが取得できること"):
            request = RequestFactory().get("/detail/1000/", data={"current_date": "2023-01-09"})
            response = self.get_response(request, user_id=1000)
            context_data = response.context_data
            self.assertQuerysetEqual(context_data["consumption_list"], [108], transform=attrgetter("consumption"))
            self.assertEqual(context_data["current_date"], "2023-01-09")
            self.assertEqual(context_data["prev_date"], "2023-01-08")
            self.assertEqual(context_data["next_date"], "2023-01-10")

        with self.subTest("データが存在しない日付を指定した場合に404エラーが出ること"):
            request = RequestFactory().get("/detail/1000/", data={"current_date": "2023-02-01"})
            with self.assertRaisesMessage(Http404, "無効な日付です。"):
                self.get_response(request, user_id=1000)

    def test_date_of_discontinuity(self):
        """ 不連続な日付でデータが作成されている場合のテスト """
        UserData.objects.create(id="1000", area="a1", tariff="t1")

        # 1日分のunixtime
        day_unixtime = 60 * 60 * 24

        # 2023-01-01, 2023-01-11日の消費量データを作成する。
        ConsumptionData.objects.bulk_create([
            ConsumptionData(
                user_id="1000",
                datetime=dt_from_unixtime(now_unixtime + 10 * day_unixtime),
                consumption=1000
            ),
            ConsumptionData(
                user_id="1000",
                datetime=dt_from_unixtime(now_unixtime + 0 * day_unixtime),
                consumption=100
            ),
        ])

        request = RequestFactory().get("/detail/1000/")
        response = self.get_response(request, user_id=1000)
        context_data = response.context_data
        self.assertEqual(context_data["user"].pk, 1000)
        with self.subTest("prev_dateに2023-01-01の日付が指定されること"):
            request = RequestFactory().get("/detail/1000/", data={"current_date": "2023-01-11"})
            response = self.get_response(request, user_id=1000)
            context_data = response.context_data
            self.assertQuerysetEqual(context_data["consumption_list"], [1000], transform=attrgetter("consumption"))
            self.assertEqual(context_data["current_date"], "2023-01-11")
            self.assertEqual(context_data["prev_date"], "2023-01-01")
            self.assertIsNone(context_data["next_date"])


class TemplateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # 消費量データなし
        cls.user = UserData.objects.create(id=1000, area="a1", tariff="t1")

        # 消費量データあり (10日分)
        cls.user2 = UserData.objects.create(id=1001, area="a1", tariff="t1")
        ConsumptionData.objects.bulk_create([
            ConsumptionData(
                user_id=1001,
                datetime=dt_from_unixtime(now_unixtime + index * day_unixtime),
                consumption=201 + index
            ) for index in range(10)
        ])

        # 消費量データあり (1日分 1時間毎10データ)
        cls.user3 = UserData.objects.create(id=1002, area="a1", tariff="t1")
        ConsumptionData.objects.bulk_create([
            ConsumptionData(
                user_id=1002,
                datetime=dt_from_unixtime(now_unixtime + index * minute_30_unixtime * 2),
                consumption=301 + index
            ) for index in range(10)
        ])

    @staticmethod
    def get_response(request, *args, **kwargs):
        view = UserDetailView()
        view.request = request
        view.args = args
        view.kwargs = kwargs
        response = view.get(request, args, kwargs)
        return response

    def test_empty_consumption_data(self):
        """ 消費量データが未登録の場合 """
        request = RequestFactory().get(f"/detail/{self.user.pk}/")
        response = self.get_response(request, user_id=self.user.pk)
        response.render()
        self.assertInHTML("<td>no data</td>", str(response.content))

    def test_per_date_consumption_data(self):
        """ 日別消費量データ """
        request = RequestFactory().get(f"/detail/{self.user2.pk}/")
        response = self.get_response(request, user_id=self.user2.pk)
        response.render()

        self.assertInHTML(
            r"""<button class="h2 btn" onclick="location.href=\'?current_date=2023-01-09\'">&laquo;</button>""",
            str(response.content))
        self.assertInHTML(r"""<td>12:00 AM</td>""", str(response.content))
        self.assertInHTML(r"""<td>210.0</td>""", str(response.content))

        with self.subTest("前日のデータに移動"):
            request = RequestFactory().get(f"/detail/{self.user2.pk}/", data={"current_date": "2023-01-09"})
            response = self.get_response(request, user_id=self.user2.pk)
            response.render()

            self.assertInHTML(
                r"""<button class="h2 btn" onclick="location.href=\'?current_date=2023-01-08\'">&laquo;</button>""",
                str(response.content))
            self.assertInHTML(
                r"""<button class="h2 btn" onclick="location.href=\'?current_date=2023-01-10\'">&raquo;</button>""",
                str(response.content))
            self.assertInHTML(r"""<td>12:00 AM</td>""", str(response.content))
            self.assertInHTML(r"""<td>209.0</td>""", str(response.content))

    def test_per_time_consumption_data(self):
        """ 時間別消費量データがある場合 """
        request = RequestFactory().get(f"/detail/{self.user3.pk}/")
        response = self.get_response(request, user_id=self.user3.pk)
        response.render()
        self.assertInHTML(r"""<td>12:00 AM</td>""", str(response.content))
        self.assertInHTML(r"""<td>09:00 AM</td>""", str(response.content))
        self.assertInHTML(r"""<td>301.0</td>""", str(response.content))
        self.assertInHTML(r"""<td>309.0</td>""", str(response.content))
        self.assertInHTML(r"""<td>310.0</td>""", str(response.content))
