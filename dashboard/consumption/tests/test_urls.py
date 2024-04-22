from django.test import TestCase
from django.urls import reverse, resolve
from ..views import SummaryView, detail


class TestUrls(TestCase):
    # summry ページテスト
    def test_summary_url_1(self):
        view = resolve('/')
        self.assertEqual(view.func.view_class, SummaryView)

    # summry ページテスト
    def test_summary_url_2(self):
        view = resolve('/summary')
        self.assertEqual(view.func.view_class, SummaryView)

    # Detail ページテスト
    def test_detail_url(self):
        url = reverse('detail', args=[1])
        self.assertEqual(resolve(url).func, detail)
        self.assertEqual(resolve(url).kwargs['user_id'], 1)
