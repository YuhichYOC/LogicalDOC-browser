from django.http import FileResponse
from django.http.response import HttpResponse

from com.yoclabo.routing import Router


def browse(request) -> HttpResponse:
    l_router = Router.LogicalDOCRouter(request)
    return l_router.run()


def download(request) -> FileResponse:
    l_router = Router.LogicalDOCRouter(request)
    return l_router.download()
