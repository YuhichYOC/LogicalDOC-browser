from django.http.response import HttpResponse

from com.yoclabo.routing import Router


def browse(request) -> HttpResponse:
    l_router = Router.BrowserRouter()
    l_router.request = request
    return l_router.run()
