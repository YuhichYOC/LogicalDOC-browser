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

from django.http.response import HttpResponse

from com.yoclabo.routing import BrowserHandler, LogicalDOCHandler


class Router:

    def __init__(self):
        self.f_request = None
        self.f_parameters: list = []

    @property
    def request(self):
        return self.f_request

    @property
    def parameters(self) -> list:
        return self.f_parameters

    @request.setter
    def request(self, arg):
        self.f_request = arg

    @parameters.setter
    def parameters(self, arg: list):
        self.f_parameters = arg

    def has_get_param(self, name: str) -> bool:
        if self.request.GET is None:
            return False
        if self.request.GET.get(name) is None:
            return False
        if not self.request.GET.get(name):
            return False
        return True

    def get_get_param(self, name: str) -> str:
        return self.request.GET.get(name)

    def has_post_param(self, name: str) -> bool:
        if self.request.POST is None:
            return False
        if self.request.POST.get(name) is None:
            return False
        if not self.request.POST.get(name):
            return False
        return True

    def run_browser_handler(self, handler: BrowserHandler) -> HttpResponse:
        handler.request = self.request
        handler.parameters = self.parameters
        return handler.run()

    def run_logicaldoc_handler(self, handler: LogicalDOCHandler, node_id: str) -> HttpResponse:
        handler.request = self.request
        handler.parameters = self.parameters
        handler.id = node_id
        return handler.run()


class BrowserRouter(Router):

    def __init__(self):
        super().__init__()

    def run(self) -> HttpResponse:
        h = BrowserHandler.BrowserHandler()
        return self.run_browser_handler(h)


class LogicalDOCRouter(Router):

    def is_root_get(self) -> bool:
        if self.has_get_param('id'):
            return False
        if self.has_get_param('type'):
            return False
        return True

    def is_folder_get(self) -> bool:
        if not self.has_get_param('id'):
            return False
        if not self.has_get_param('type'):
            return False
        if not self.has_get_param('page'):
            return False
        if self.get_get_param('type') != 'folder':
            return False
        return True

    def is_folder_create(self) -> bool:
        if not self.has_post_param('id'):
            return False
        if not self.has_post_param('folderName'):
            return False
        return True

    def is_document_create(self) -> bool:
        if not self.has_post_param('id'):
            return False
        if len(self.request.FILES) == 0:
            return False
        if self.request.FILES is None:
            return False
        if self.request.FILES['file'] is None:
            return False
        return True

    def is_document_page_feed(self) -> bool:
        if not self.has_get_param('id'):
            return False
        if not self.has_get_param('type'):
            return False
        if not self.has_get_param('page'):
            return False
        if self.get_get_param('type') != 'pdf':
            return False
        return True

    def respond_root(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCRootFolderHandler()
        return self.run_logicaldoc_handler(h, '')

    def respond_folder(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCFolderHandler()
        return self.run_logicaldoc_handler(h, self.get_get_param('id'))

    def respond_folder_create(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCCreateFolderHandler()
        return self.run_logicaldoc_handler(h, '')

    def respond_document_create(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCCreateDocumentHandler()
        return self.run_logicaldoc_handler(h, '')

    def respond_document(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCDocumentHandler()
        return self.run_logicaldoc_handler(h, self.get_get_param('id'))

    def respond_document_page_feed(self) -> HttpResponse:
        h = LogicalDOCHandler.LogicalDOCDocumentPageFeedHandler()
        return self.run_logicaldoc_handler(h, self.get_get_param('id'))

    def run(self) -> HttpResponse:
        if self.is_folder_create():
            return self.respond_folder_create()
        if self.is_document_create():
            return self.respond_document_create()
        if self.is_root_get():
            return self.respond_root()
        if self.is_folder_get():
            return self.respond_folder()
        if self.is_document_page_feed():
            return self.respond_document_page_feed()
        return self.respond_document()
