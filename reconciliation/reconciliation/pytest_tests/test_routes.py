from http import HTTPStatus

from django.urls import reverse
from django.urls.exceptions import NoReverseMatch


def test_login_redirect(client, url_names, mocker):
    """Тест редиректа на страницу входа в аккаунт."""

    mocker.patch("django.shortcuts.get_object_or_404")
    for name in url_names:
        try:
            url = reverse(name)
        except NoReverseMatch:
            url = reverse(name, args=(1,))
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert "/accounts/login/" in response.url
