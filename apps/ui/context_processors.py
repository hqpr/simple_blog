from django.conf import settings


def search_url(request):
    return {'search_url': settings.DEFAULT_SEARCH_ENGINE}
