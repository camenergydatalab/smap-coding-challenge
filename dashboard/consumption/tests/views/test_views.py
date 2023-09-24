from django.test import TestCase
from django.urls import reverse
from consumption.models import User, AggregateUserDailyConsumption
from datetime import date

class SummaryViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(id=1, area="a1", tariff="t1")
        self.user2 = User.objects.create(id=2, area="a2", tariff="t2")

        AggregateUserDailyConsumption.objects.create(
            user=self.user1,
            date='2023-09-10',
            total_consumption='100.50',
            average_consumption='50.25'
        )
        AggregateUserDailyConsumption.objects.create(
            user=self.user2,
            date='2023-09-11',
            total_consumption='200.75',
            average_consumption='66.92'
        )

    def test_summary_view(self):
        # summaryビューを呼び出し
        response = self.client.get(reverse('summary'))

        # 正しいHTTPステータスコード（200 OK）が返されることを確認
        self.assertEqual(response.status_code, 200)

        # テンプレートに渡されるコンテキストが正しいことを確認
        self.assertQuerysetEqual(
            response.context['users'],
            ['<User: User object (1)>', '<User: User object (2)>'],
            ordered=False
        )

        # コンテキストからデータを取得
        context_data = response.context['date_wise_consumption_data']

        # リスト内のデータ数を確認
        self.assertEqual(len(context_data), 2)

        # 各データを個別に比較
        self.assertEqual(context_data[0]['date'], date(2023, 9, 10))
        self.assertEqual(context_data[0]['total_consumption'], 100.5)
        self.assertEqual(context_data[0]['average_consumption'], 50.25)

        self.assertEqual(context_data[1]['date'], date(2023, 9, 11))
        self.assertEqual(context_data[1]['total_consumption'], 200.75)
        self.assertEqual(context_data[1]['average_consumption'], 66.92)

class DetailViewTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(id=1, area="a1", tariff="t1")

        AggregateUserDailyConsumption.objects.create(
            user=self.user1,
            date='2023-09-10',
            total_consumption='100.50',
            average_consumption='50.25'
        )
        AggregateUserDailyConsumption.objects.create(
            user=self.user1,
            date='2023-09-11',
            total_consumption='200.75',
            average_consumption='66.92'
        )

    def test_detail_view(self):
        # detailビューを呼び出し（ユーザーIDを指定）
        response = self.client.get(reverse('detail', args=(self.user1.id,)))

        # 正しいHTTPステータスコード（200 OK）が返されることを確認
        self.assertEqual(response.status_code, 200)

        # テンプレートに渡されるコンテキストが正しいことを確認
        self.assertEqual(response.context['user'], self.user1)

        self.assertQuerysetEqual(
            response.context['date_wise_consumption_data'],
            [
                '<AggregateUserDailyConsumption: AggregateUserDailyConsumption object (1)>',
                '<AggregateUserDailyConsumption: AggregateUserDailyConsumption object (2)>'
            ],
            ordered=False
        )
