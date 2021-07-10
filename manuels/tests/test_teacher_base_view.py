from django.test import TestCase
from model_bakery import baker

from manuels.tests.selenium import TeacherSeleniumTestCase, TeacherTestMixin


class TeacherBaseViewTestCase(TeacherTestMixin, TestCase):
    def test_view_is_rendered(self):
        url = self.teacher.get_absolute_url()
        res = self.client.get(url)
        assert res.status_code == 200

    def view_is_passed_teacher(self):
        baker.make_recipe("manuels.tests.book", _quantity=5, teacher=self.teacher)
        baker.make_recipe("manuels.tests.book", _quantity=5)
        baker.make_recipe("manuels.tests.supply", _quantity=5, teacher=self.teacher)
        baker.make_recipe("manuels.tests.supply", _quantity=5)
        url = self.teacher.get_absolute_url()
        res = self.client.get(url)
        assert res.status_code == 200
        assert res.context["teacher"] == self.teacher


class TeacherBaseViewSeleniumTestCase(TeacherSeleniumTestCase):
    def test_books_are_displayed(self):
        teacher_books = baker.make_recipe(
            "manuels.tests.book", _quantity=5, teacher=self.teacher
        )
        other_books = baker.make_recipe("manuels.tests.book", _quantity=5)
        url = self.teacher.get_absolute_url()
        self.get(url)
        for book in teacher_books:
            assert book.title in self.selenium.page_source
        for book in other_books:
            assert book.title not in self.selenium.page_source

    def test_supplies_are_displayed(self):
        teacher_supplies = baker.make_recipe(
            "manuels.tests.supply", _quantity=5, teacher=self.teacher
        )
        other_supplies = baker.make_recipe("manuels.tests.supply", _quantity=5)
        url = self.teacher.get_absolute_url()
        self.get(url)
        for supply in teacher_supplies:
            assert supply.supplies in self.selenium.page_source
        for supply in other_supplies:
            assert supply.supplies not in self.selenium.page_source
