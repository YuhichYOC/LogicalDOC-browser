from django.http.response import HttpResponse

from com.yoclabo.routing import Router


def browse(request) -> HttpResponse:
    l_router = Router.LogicalDOCRouter()
    l_router.request = request
    return l_router.run()
