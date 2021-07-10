from datetime import datetime

from django.test import LiveServerTestCase
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver

from manuels.models import Teacher


class SeleniumTestCase(LiveServerTestCase):
    headless = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        if cls.headless:
            options.add_argument("-headless")
        cls.selenium = WebDriver(options=options)
        cls.selenium.implicitly_wait(10)
        cls.addClassCleanup(cls._cleanup_selenium)

    @classmethod
    def _cleanup_selenium(cls):
        try:
            cls.selenium.quit()
        finally:
            # Explicitly ignore errors, we just want to try and quit if it exists.
            pass

    def tearDown(self):
        for method, error in self._outcome.errors:
            if error:
                now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
                name = f"pytest_result/assets/screenshot-{now}-{str(self)}.png"
                self.selenium.get_screenshot_as_file(name)

    def get(self, url):
        self.selenium.get(self.get_full_url(url))

    def get_full_url(self, url):
        return f"{self.live_server_url}{url}"


class TeacherTestMixin:
    def setUp(self) -> None:
        super().setUp()
        self.teacher = Teacher.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="0000000000",
            email="teacher@example.com",
        )


class TeacherSeleniumTestCase(TeacherTestMixin, SeleniumTestCase):
    pass
