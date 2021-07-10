from django.test import TestCase

from manuels.tests.selenium import TeacherSeleniumTestCase


class TeacherBaseViewTestCase(TestCase):
    def test_view_is_rendered(self):
        # Go to url
        # check response is 200
        assert False

    def test_view_contains_books(self):
        # Create books linked to teacher
        # go to url
        # check response is 200
        # check books are in context
        assert False

    def test_view_contains_supplies(self):
        # create supplies requirements linked to teacher
        # go to url
        # check response is 200
        # check supplies are in context
        assert False


class TeacherBaseViewSeleniumTestCase(TeacherSeleniumTestCase):
    def test_books_are_displayed(self):
        # Create books linked to teacher
        # go to url
        # check book title is displayed
        assert False

    def test_supplies_are_displayed(self):
        # Create books linked to teacher
        # go to url
        # check supplies name is displayed
        assert False
