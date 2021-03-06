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
        self.f_id: str = ''

    @property
    def request(self):
        return self.f_request

    @property
    def parameters(self) -> list:
        return self.f_parameters

    @property
    def id(self) -> str:
        return self.f_id

    @request.setter
    def request(self, arg):
        self.f_request = arg

    @parameters.setter
    def parameters(self, arg: list):
        self.f_parameters = arg

    @id.setter
    def id(self, arg: str):
        self.f_id = arg

    @staticmethod
    def query_root_folder() -> dict:
        l_f = Folder()
        l_f.type = 'folder'
        l_f.go_to_root()
        return {'folder': l_f}

    def query_folder(self) -> dict:
        l_f = Folder()
        l_f.id = self.id
        l_f.type = 'folder'
        if self.request.GET.get('tile') is not None:
            l_f.is_tile = True
        l_f.go_to_page(int(self.request.GET.get('page')))
        return {'folder': l_f}

    def fetch_thumb(self) -> str:
        l_d = Image()
        l_d.id = str(self.id)
        l_d.type = self.request.GET.get('type')
        l_d.fetch_thumb()
        return l_d.thumb

    def query_document(self) -> dict:
        l_d = AbstractDocument.new(self.id, self.request.GET.get('type'), '', True)
        return {'document': l_d}

    def query_document_page_feed(self) -> dict:
        l_d = Pdf()
        l_d.id = self.id
        l_d.go_to_page(int(self.request.GET.get('page')))
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
        self.id = self.request.POST['id']
        l_q = Query.FolderQuery()
        l_q.id = self.id
        l_q.create_folder(self.request.POST['folderName'])
        return render(self.request, 'logicaldoc/browse.html', self.query_folder())


class LogicalDOCCreateDocumentHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        self.id = self.request.POST['id']
        l_q = Query.FolderQuery()
        l_q.id = self.id
        l_q.create_document('jp', self.request.FILES['file'].name, self.request.FILES['file'])
        return render(self.request, 'logicaldoc/browse.html', self.query_folder())


class LogicalDOCDocumentHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        return render(self.request, 'logicaldoc/view.html', self.query_document())


class LogicalDOCDocumentPageFeedHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        return render(self.request, 'logicaldoc/view.html', self.query_document_page_feed())
