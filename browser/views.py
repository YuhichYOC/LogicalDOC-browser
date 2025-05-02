from django.http.response import HttpResponse

from com.yoclabo.routing import Router


def browse(request) -> HttpResponse:
    l_router = Router.BrowserRouter(request)
    return l_router.run()
