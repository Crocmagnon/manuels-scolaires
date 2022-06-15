from django.core import mail
from django.urls import reverse

from manuels.models import Teacher
from manuels.tests.selenium import SeleniumTestCase


class InscriptionTestCase(SeleniumTestCase):
    def setUp(self) -> None:
        super().setUp()
        url = reverse("home_page")
        assert Teacher.objects.count() == 0
        self.get(url)
        self.selenium.find_element_by_id("id_first_name").send_keys("John")
        self.selenium.find_element_by_id("id_last_name").send_keys("Doe")
        self.selenium.find_element_by_id("id_phone_number").send_keys("0123456789")
        self.selenium.find_element_by_id("id_email").send_keys("john@doe.com")
        self.selenium.find_element_by_css_selector(".btn[type=submit]").click()
        self.teacher = Teacher.objects.first()
        expected_url = self.teacher.get_absolute_url()
        self.expected_url = self.get_full_url(expected_url)

    def test_teacher_is_created(self):
        assert self.teacher.first_name == "John"
        assert self.teacher.last_name == "Doe"
        assert self.teacher.phone_number == "0123456789"
        assert self.teacher.email == "john@doe.com"

    def test_user_is_redirected(self):
        assert self.selenium.current_url == self.expected_url

    def test_email_is_sent(self):
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.subject == "Gestion des manuels scolaires"
        assert self.expected_url in email.body

    def test_logged_in_user_is_redirected(self):
        url = reverse("home_page")
        self.get(url)
        expected_url = self.teacher.get_absolute_url()
        expected_url = self.get_full_url(expected_url)
        assert self.selenium.current_url == expected_url
