#
# LogicalDOCHandler.py
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
from django.shortcuts import render

from com.yoclabo.logicaldoc.item.Item import AbstractDocument, Image, Folder, Pdf
from com.yoclabo.logicaldoc.query import Query


class LogicalDOCHandler:

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
        return self.request.GET.get(name) is not None

    def has_post_param(self, name: str) -> bool:
        return self.request.POST.get(name) is not None

    def has_files_param(self, name: str) -> bool:
        return self.request.FILES.get(name) is not None

    def get_param(self, name: str) -> str:
        if self.has_post_param(name):
            return self.request.POST.get(name)
        return self.request.GET.get(name)

    def get_files(self, name: str):
        if self.has_files_param(name):
            return self.request.FILES.get(name)
        return None

    @staticmethod
    def query_root_folder() -> dict:
        l_f = Folder()
        l_f.type = 'folder'
        l_f.go_to_root()
        return {'folder': l_f}

    def query_folder(self) -> dict:
        l_f = Folder()
        l_f.id = self.get_param('id')
        l_f.type = 'folder'
        if self.has_get_param('tile'):
            l_f.is_tile = True
        elif self.has_post_param('tile'):
            l_f.is_tile = True
        l_f.go_to_page(int(self.get_param('page')))
        return {'folder': l_f}

    def fetch_thumb(self) -> str:
        l_d = Image()
        l_d.id = str(self.get_param('id'))
        l_d.type = self.get_param('type')
        l_d.fetch_thumb()
        return l_d.thumb

    def folder_create(self) -> dict:
        l_q = Query.FolderQuery()
        l_q.id = self.get_param('id')
        l_q.create_folder(self.get_param('folderName'))
        return self.query_folder()

    def document_create(self) -> dict:
        l_q = Query.FolderQuery()
        l_q.id = self.get_param('id')
        l_q.create_document('jp', self.get_files('file').name, self.get_files('file'))
        return self.query_folder()

    def query_document(self) -> dict:
        l_d = AbstractDocument.new(self.get_param('id'), self.get_param('type'), '', True)
        return {'document': l_d}

    def query_document_page_feed(self) -> dict:
        l_d = Pdf()
        l_d.id = self.get_param('id')
        l_d.go_to_page(int(self.get_param('page')))
        return {'document': l_d}

    def run(self):
        pass


class LogicalDOCRootFolderHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        return render(self.request, 'logicaldoc/browse.html', self.query_root_folder())


class LogicalDOCFolderHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        return render(self.request, 'logicaldoc/browse.html', self.query_folder())


class LogicalDOCThumbHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        return HttpResponse(self.fetch_thumb(), content_type='text/plain')


class LogicalDOCCreateFolderHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        return render(self.request, 'logicaldoc/browse.html', self.folder_create())


class LogicalDOCCreateDocumentHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        return render(self.request, 'logicaldoc/browse.html', self.document_create())


class LogicalDOCDocumentHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        return render(self.request, 'logicaldoc/view.html', self.query_document())


class LogicalDOCDocumentPageFeedHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        return render(self.request, 'logicaldoc/view.html', self.query_document_page_feed())
