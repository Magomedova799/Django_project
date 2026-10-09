from django.test import TestCase
from django.urls import reverse

class BlogSimpleTests(TestCase):
    def test_home_page_status_code(self):
        '''Проверяем, что главная страница сайта успешно открывается'''
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

