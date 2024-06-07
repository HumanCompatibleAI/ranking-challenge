import pytest


def pytest_addoption(parser):
    parser.addoption("--url", action="store")


# create a url fixture that can be passed from the command line
@pytest.fixture(scope="session")
def url(request):
    url_value = request.config.option.url
    if url_value is None:
        pytest.skip()
    return url_value
