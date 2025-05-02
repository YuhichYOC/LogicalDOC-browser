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

from django.core.handlers.wsgi import WSGIRequest
from django.http import FileResponse
from django.http.response import HttpResponse
from django.shortcuts import render

from com.yoclabo.logicaldoc.item.Item import Item, Directory, Text, Image, Pdf, Media
from com.yoclabo.logicaldoc.query.Query import ITEM_TYPE_TEXT, ITEM_TYPE_IMAGE, ITEM_TYPE_PDF, ITEM_TYPE_MEDIA


def go_to_root(page: int, tile: bool) -> dict:
    l_d = Directory('', '', 1)
    l_d.prepare_browse(page, tile)
    return {'directory': l_d}


def go_to_directory(id: str, name: str, page: int, tile: bool) -> dict:
    l_d = Directory(id, name, 1)
    l_d.prepare_browse(page, tile)
    return {'directory': l_d}


def create_directory(id: str, parent_name: str, child_name: str) -> None:
    l_d = Directory(id, parent_name, 1)
    l_d.create_directory(child_name)
    return


def create_text_file(id: str, parent_name: str, child_name: str, content: str) -> None:
    l_d = Directory(id, parent_name, 1)
    l_d.create_text_file(child_name, content)
    return


def save_file(id: str, parent_name: str, files: dict) -> None:
    l_d = Directory(id, parent_name, 1)
    l_d.save_file(files)
    return


def view_text(id: str, name: str) -> dict:
    l_t = Text(id, name, 1)
    l_t.prepare_view()
    return {'document': l_t}


def update_text_content(id: str, name: str, new_content: str) -> None:
    l_t = Text(id, name, 1)
    l_t.update_text_content(new_content)
    return


def view_image(id: str, name: str) -> dict:
    l_i = Image(id, name, 1)
    l_i.prepare_view()
    return {'document': l_i}


def view_pdf(id: str, name: str) -> dict:
    l_p = Pdf(id, name, 1)
    l_p.prepare_view()
    return {'document': l_p}


def view_media(id: str, name: str) -> dict:
    l_m = Media(id, name, 1)
    l_m.prepare_view()
    return {'document': l_m}


def view_others(id: str, type: str, name: str) -> dict:
    l_o = Item(id, type, name, 1)
    l_o.fill_ancestors()
    return {'document': l_o}


def get_web_encoded_image(id: str) -> str:
    l_i = Image(id, '', 1)
    return l_i.get_web_encoded_image()


def get_image_bytearray(id: str) -> bytes:
    l_i = Image(id, '', 1)
    return l_i.get_image_bytearray()


class LogicalDOCHandler:

    def __init__(self, request: WSGIRequest) -> None:
        self.f_request: WSGIRequest = request
        return

    @property
    def request(self) -> WSGIRequest:
        return self.f_request

    def has_get_param(self, name: str) -> bool:
        return self.request.GET.get(name) is not None

    def has_post_param(self, name: str) -> bool:
        return self.request.POST.get(name) is not None

    def get_param(self, name: str) -> str:
        if self.has_post_param(name):
            return self.request.POST.get(name)
        return self.request.GET.get(name)

    def run(self) -> None:
        pass


class LogicalDOCImageBytearrayHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        return HttpResponse(get_image_bytearray(self.get_param('id')), content_type='application/octet-stream')


class LogicalDOCWebEncodedImageHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        return HttpResponse(get_web_encoded_image(self.get_param('id')), content_type='text/plain')


class LogicalDOCUpdateTextContentHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        update_text_content(self.get_param('id'), self.get_param('name'), self.get_param('text_content'))
        h = LogicalDOCDocumentHandler(self.request)
        return h.run()


class LogicalDOCDocumentHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        if self.get_param('type') == ITEM_TYPE_TEXT:
            return render(
                self.request, 'logicaldoc/view.html', view_text(self.get_param('id'), self.get_param('name'))
            )
        if self.get_param('type') == ITEM_TYPE_IMAGE:
            return render(
                self.request, 'logicaldoc/view.html', view_image(self.get_param('id'), self.get_param('name'))
            )
        if self.get_param('type') == ITEM_TYPE_PDF:
            return render(
                self.request, 'logicaldoc/view.html', view_pdf(self.get_param('id'), self.get_param('name'))
            )
        if self.get_param('type') == ITEM_TYPE_MEDIA:
            return render(
                self.request, 'logicaldoc/view.html', view_media(self.get_param('id'), self.get_param('name'))
            )
        return render(
            self.request, 'logicaldoc/view.html',
            view_others(self.get_param('id'), self.get_param('type'), self.get_param('name'))
        )


class LogicalDOCDownloadHandler(LogicalDOCHandler):

    def run(self) -> FileResponse:
        return FileResponse(get_image_bytearray(self.get_param('id')))


class LogicalDOCFilePostHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        save_file(self.get_param('id'), self.get_param('name'), self.request.FILES)
        h = LogicalDOCDirectoryHandler(self.request) if self.has_get_param('id') \
            else LogicalDOCRootDirectoryHandler(self.request)
        return h.run()


class LogicalDOCCreateTextFileHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        create_text_file(
            self.get_param('id'), self.get_param('name'), self.get_param('textFileName'), self.get_param('content')
        )
        h = LogicalDOCDirectoryHandler(self.request) if self.has_get_param('id') \
            else LogicalDOCRootDirectoryHandler(self.request)
        return h.run()


class LogicalDOCCreateDirectoryHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        create_directory(self.get_param('id'), self.get_param('name'), self.get_param('directoryName'))
        h = LogicalDOCDirectoryHandler(self.request) if self.has_get_param('id') \
            else LogicalDOCRootDirectoryHandler(self.request)
        return h.run()


class LogicalDOCDirectoryHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        l_page: int = 1
        if self.has_get_param('page'):
            l_page = int(self.get_param('page'))
        l_tile: bool = False
        if self.has_get_param('tile'):
            l_tile = bool(self.get_param('tile'))
        return render(
            self.request, 'logicaldoc/browse.html',
            go_to_directory(self.get_param('id'), self.get_param('name'), l_page, l_tile)
        )


class LogicalDOCRootDirectoryHandler(LogicalDOCHandler):

    def run(self) -> HttpResponse:
        l_page: int = 1
        if self.has_get_param('page'):
            l_page = int(self.get_param('page'))
        l_tile: bool = False
        if self.has_get_param('tile'):
            l_tile = bool(self.get_param('tile'))
        return render(
            self.request, 'logicaldoc/browse.html', go_to_root(l_page, l_tile)
        )
