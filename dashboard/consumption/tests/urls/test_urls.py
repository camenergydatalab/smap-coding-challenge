from django.test import TestCase
from django.urls import reverse
from consumption.models import User

class URLPatternTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(id=1, area="a1", tariff="t1")

    def test_summary_url(self):
        url = reverse('summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'consumption/summary.html')

    def test_detail_url(self):
        user_id = 1
        url = reverse('detail', args=[user_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'consumption/detail.html')
