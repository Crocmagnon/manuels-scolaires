import pytest
from django.core.management import call_command


@pytest.fixture(autouse=True, scope="session")
def _collect_static() -> None:
    call_command("collectstatic", "--no-input", "--clear")
