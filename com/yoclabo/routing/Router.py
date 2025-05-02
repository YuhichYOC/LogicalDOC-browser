#
# Router.py
#
# Copyright 2021 Yuichi Yoshii
#     吉井雄一 @ 吉井産業  you.65535.kir@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from django.core.handlers.wsgi import WSGIRequest
from django.http import FileResponse
from django.http.response import HttpResponse

from com.yoclabo.logicaldoc.query.Query import ITEM_TYPE_DIRECTORY, ITEM_TYPE_IMAGE
from com.yoclabo.routing import BrowserHandler, LogicalDOCHandler


def run_browser_handler(handler: BrowserHandler) -> HttpResponse:
    return handler.run()


def run_logicaldoc_handler(handler: LogicalDOCHandler) -> HttpResponse | FileResponse:
    return handler.run()


class Router:

    def __init__(self, request: WSGIRequest) -> None:
        self.f_request: WSGIRequest = request
        return

    @property
    def request(self) -> WSGIRequest:
        return self.f_request

    def has_get_param(self, name: str) -> bool:
        if self.request.GET.get(name) is None:
            return False
        if not self.request.GET.get(name):
            return False
        return True

    def has_post_param(self, name: str) -> bool:
        if self.request.POST.get(name) is None:
            return False
        if not self.request.POST.get(name):
            return False
        return True

    def get_param(self, name: str) -> str:
        if self.has_post_param(name):
            return self.request.POST.get(name)
        return self.request.GET.get(name)


class BrowserRouter(Router):

    def __init__(self, request: WSGIRequest) -> None:
        super().__init__(request)
        return

    def run(self) -> HttpResponse:
        h = BrowserHandler.BrowserHandler(self.request)
        return run_browser_handler(h)


class LogicalDOCRouter(Router):

    def __init__(self, request: WSGIRequest):
        super().__init__(request)

    def is_file_post(self) -> bool:
        if not self.request.method == 'POST':
            return False
        if not self.request.FILES:
            return False
        # If the parameter id is blank, I assume it's a post to the root directory.
        return True

    def is_text_update_post(self) -> bool:
        if not self.request.method == 'POST':
            return False
        if not self.has_post_param('text_content'):
            return False
        return True

    def is_create_text_file_post(self) -> bool:
        if not self.request.method == 'POST':
            return False
        if not self.has_post_param('textFileName'):
            return False
        if not self.has_post_param('content'):
            return False
        return True

    def is_create_directory_post(self) -> bool:
        if not self.request.method == 'POST':
            return False
        if not self.has_post_param('directoryName'):
            return False
        return True

    def is_image_bytearray_get(self) -> bool:
        if not self.has_get_param('id'):
            return False
        if not self.has_get_param('content'):
            return False
        if self.get_param('content') != 'bytes':
            return False
        return True

    def is_web_encoded_image_get(self) -> bool:
        if not self.has_get_param('id'):
            return False
        if not self.has_get_param('content'):
            return False
        if self.get_param('content') != 'encoded':
            return False
        return True

    def is_document_get(self) -> bool:
        if not self.has_get_param('id'):
            return False
        if not self.has_get_param('type'):
            return False
        if self.get_param('type') == ITEM_TYPE_DIRECTORY:
            return False
        if self.get_param('type') == ITEM_TYPE_IMAGE:
            if self.has_get_param('content'):
                return False
        return True

    def is_directory_get(self) -> bool:
        if not self.has_get_param('id'):
            return False
        return True

    def is_root_get(self) -> bool:
        if len(self.request.POST) > 0:
            return False
        if len(self.request.GET) > 0:
            if self.get_param('id') != '':
                return False
        return True

    def respond_post_file(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCFilePostHandler(self.request)
        return run_logicaldoc_handler(h)

    def respond_file_download(self) -> FileResponse:
        h = LogicalDOCHandler.LogicalDOCDownloadHandler(self.request)
        return run_logicaldoc_handler(h)

    def respond_update_text_content(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCUpdateTextContentHandler(self.request)
        return run_logicaldoc_handler(h)

    def respond_image_bytearray(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCImageBytearrayHandler(self.request)
        return run_logicaldoc_handler(h)

    def respond_web_encoded_image(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCWebEncodedImageHandler(self.request)
        return run_logicaldoc_handler(h)

    def respond_document(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCDocumentHandler(self.request)
        return run_logicaldoc_handler(h)

    def respond_create_text_file(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCCreateTextFileHandler(self.request)
        return run_logicaldoc_handler(h)

    def respond_create_directory(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCCreateDirectoryHandler(self.request)
        return run_logicaldoc_handler(h)

    def respond_directory(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCDirectoryHandler(self.request)
        return run_logicaldoc_handler(h)

    def respond_root(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCRootDirectoryHandler(self.request)
        return run_logicaldoc_handler(h)

    def run(self) -> HttpResponse:
        if self.is_file_post():
            return self.respond_post_file()
        if self.is_text_update_post():
            return self.respond_update_text_content()
        if self.is_create_text_file_post():
            return self.respond_create_text_file()
        if self.is_create_directory_post():
            return self.respond_create_directory()
        if self.is_image_bytearray_get():
            return self.respond_image_bytearray()
        if self.is_web_encoded_image_get():
            return self.respond_web_encoded_image()
        if self.is_document_get():
            return self.respond_document()
        if self.is_directory_get():
            return self.respond_directory()
        if self.is_root_get():
            return self.respond_root()
        h = BrowserHandler.BrowserHandler(self.request)
        return run_browser_handler(h)

    def download(self) -> FileResponse:
        return self.respond_file_download()
