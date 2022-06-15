from pathlib import Path

import vcr
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from manuels.models import Book, Editor
from manuels.tests.selenium import TeacherSeleniumTestCase


class AddBookTestCase(TeacherSeleniumTestCase):
    fixtures = ["editors", "levels"]

    @vcr.use_cassette(
        str((Path(__file__).parent / "cassettes/add_book_with_decitre.yaml").resolve()),
        ignore_localhost=True,
    )
    def test_add_book_with_decitre(self):
        field = "Français"
        isbn = "978-2-216-15739-6"
        title = "Français CAP Les nouveaux cahiers"
        authors = (
            "Michèle Sendre-Haïdar,Nathalie Leduc,Florian Seuzaret,Emmanuelle Goulard"
        )
        price = 17.5
        editor = Editor.objects.get(name__iexact="Foucher")

        self.get(self.teacher.get_absolute_url())
        self.selenium.find_element_by_id("add-book").click()
        self.selenium.find_element_by_id("id_levels").send_keys("TEPC")
        self.selenium.find_element_by_id("id_field").send_keys(field)
        self.selenium.find_element_by_id("id_isbn").send_keys(isbn)
        self.selenium.find_element_by_id("id_isbn_button").click()

        self._wait_for_elements_by_css_selector("#id_isbn.is-valid")
        self.assert_input_value("id_title", title)
        self.assert_input_value("id_publication_year", "2020")
        self.assert_input_value("id_editor", editor.pk)
        self.assert_input_value("id_authors", authors)
        self.assert_input_value("id_price", str(price))

        self.selenium.find_element_by_id("id_previously_acquired").send_keys("Non")
        self.selenium.find_element_by_id("id_consumable").send_keys("Non")
        self.selenium.find_element_by_css_selector("[for=id_add_another]").click()
        self.selenium.find_element_by_css_selector(".btn[type=submit]").click()

        expected_url = self.teacher.get_absolute_url()
        expected_url = self.get_full_url(expected_url)
        assert self.selenium.current_url == expected_url

        book = Book.objects.first()
        assert book.teacher == self.teacher
        assert book.isbn == isbn
        assert book.field == field
        assert book.title == title
        assert book.publication_year == 2020
        assert book.editor == editor
        assert book.authors == authors
        assert book.previously_acquired is False
        assert book.consumable is False

    def assert_input_value(self, input_id, expected_value):
        assert self.selenium.find_element_by_id(input_id).get_attribute("value") == str(
            expected_value
        )

    def _wait_for_elements_by_css_selector(self, css_selector, wait_time=5):
        wait = WebDriverWait(self.selenium, wait_time)
        markers = wait.until(
            expected_conditions.presence_of_all_elements_located(
                (By.CSS_SELECTOR, css_selector)
            )
        )
        return markers
