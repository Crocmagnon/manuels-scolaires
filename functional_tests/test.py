import time

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

MAX_WAIT = 10


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        # Edith has received a mail from her librarian about a website
        # she can use to tell the books she needs. She goes
        # to check out its homepage
        self.browser.get(self.live_server_url)

        # She notices the page title and header mention "manuels"
        self.assertIn('Manuels', self.browser.title)

        # She is invited to enter her contact information (first name,
        # last name and phone number)
        # She types "Edith" into the first name text box

        # She types "Doe" as her last name

        # She types "0612345678" as her phone number

        # When she hits enter, the page updates, and now the page displays
        # her contact info on top and a form to enter book data

        # Edith wonders whether the site will remember her books. Then she sees
        # that the site has generated a unique URL for her -- there is some
        # explanatory text to that effect.

        # She visits that URL - her books list is still there.

        # Satisfied, she goes back to sleep
        self.fail('Finish the test!')

    def wait_for(self, fn):
        start_time = time.time()
        while True:
            try:
                return fn()
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)
