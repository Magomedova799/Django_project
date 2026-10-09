from django.test import TestCase
from django.urls import reverse

class AccountSimpleTests(TestCase):
    def test_login_page_status_code(self):
        '''Проверяем, что страница входа в аккаунт успешно открывается'''
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_status_code(self):
        '''Проверяем, что страница регистрации успешно открывается'''
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

