from url import URL
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def test_scheme():
    url = URL("https://example.com")
    assert url.scheme == "https"
    assert url.isHttps == True

    url = URL("http://example.com")
    assert url.scheme == "http"
    assert url.isHttps == False


def test_host():
    url = URL("https://example.com")
    assert url.host == "example.com"

    url = URL("http://test.org")
    assert url.host == "test.org"


def test_port():
    url = URL("http://example.com")
    assert url.port == 80

    url = URL("https://example.com")
    assert url.port == 443

    url = URL("https://example.com:8080")
    assert url.port == 8080


def test_path():
    url = URL("http://example.com/some-page")
    assert url.path == "/some-page"

    url = URL("https://example.com")
    assert url.path == "/"
