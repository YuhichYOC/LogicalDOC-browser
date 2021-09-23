#
# Item.py
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

import base64
import os

import PyPDF4

from browser.settings import BASE_DIR
from com.yoclabo.logicaldoc.query.Query import DocumentQuery, FolderQuery


class AbstractItem:

    def __init__(self):
        self.f_id: str = ''
        self.f_type: str = ''
        self.f_name: str = ''
        self.f_ancestors: list = []
        self.f_sequence: int = 0

    @property
    def id(self) -> str:
        return self.f_id

    @property
    def type(self) -> str:
        return self.f_type

    @property
    def name(self) -> str:
        return self.f_name

    @property
    def ancestors(self) -> list:
        return self.f_ancestors

    @property
    def sequence(self) -> int:
        return self.f_sequence

    @property
    def is_even_row(self) -> bool:
        return 0 == self.f_sequence % 2

    @id.setter
    def id(self, arg: str):
        self.f_id = arg

    @type.setter
    def type(self, arg: str):
        self.f_type = arg

    @name.setter
    def name(self, arg: str):
        self.f_name = arg

    @sequence.setter
    def sequence(self, arg: int):
        self.f_sequence = arg

    def fill_ancestors(self, folder_id: str) -> None:
        self.f_ancestors.clear()
        l_fq = FolderQuery()
        l_fq.id = folder_id
        for a in l_fq.get_path():
            self.f_ancestors.append(Folder.new(str(a['id']), 'folder', a['name']))
        if 'folder' == self.f_type:
            del self.f_ancestors[-1]
        return None


class Folder(AbstractItem):

    def __init__(self):
        super().__init__()
        self.f_children: list = []
        self.f_page: int = 0
        self.f_pages: list = []
        self.f_is_tile: bool = False
        self.ITEMS_PER_PAGE: int = 10
        self.TILE_ITEMS_PER_PAGE: int = 30

    @property
    def children(self) -> list:
        return self.f_children

    @property
    def pages(self) -> list:
        return self.f_pages

    @property
    def page(self) -> int:
        return self.f_page

    @property
    def max_page(self) -> int:
        if 0 == len(self.f_children):
            return 1
        if self.is_tile:
            return -(-len(self.f_children) // self.TILE_ITEMS_PER_PAGE)
        # Round up len(self.f_children) divided by "ITEMS_PER_PAGE" to get the maximum number of pages.
        return -(-len(self.f_children) // self.ITEMS_PER_PAGE)

    @property
    def prev_page(self) -> int:
        return self.f_page - 1 if 1 < self.f_page else 1

    @property
    def next_page(self) -> int:
        return self.f_page + 1 if self.max_page > self.f_page else self.max_page

    @property
    def is_tile(self) -> bool:
        return self.f_is_tile

    @is_tile.setter
    def is_tile(self, arg: bool):
        self.f_is_tile = arg

    @staticmethod
    def new(a_id: str, a_type: str, a_name: str):
        l_f = Folder()
        l_f.id = a_id
        l_f.type = a_type
        l_f.name = a_name
        return l_f

    def describe_root_folder(self) -> None:
        l_fq = FolderQuery()
        l_fq.path = '/'
        self.id = str(l_fq.find_by_path()['id'])
        self.describe()
        return None

    def describe(self) -> None:
        self.f_children.clear()
        l_fq = FolderQuery()
        l_fq.id = self.id
        self.name = l_fq.get_folder()['name']
        for f in l_fq.list_children():
            l_add = Folder.new(str(f['id']), 'folder', f['name'])
            l_add.sequence = len(self.f_children) + 1
            self.f_children.append(l_add)
        for d in l_fq.list_document():
            l_add = AbstractDocument.new(str(d['id']), d['type'], d['fileName'])
            l_add.sequence = len(self.f_children) + 1
            self.f_children.append(l_add)
        self.f_page = 1
        self.f_pages = Paginator().create_list(1, self.prev_page, self.next_page, self.max_page)
        self.fill_ancestors(self.id)
        return None

    def go_to_page(self, arg: int) -> None:
        self.f_page = arg
        self.f_page = 1 if 1 > self.f_page else self.f_page
        self.f_page = self.max_page if self.max_page < self.f_page else self.f_page
        self.f_pages = Paginator().create_list(self.f_page, self.prev_page, self.next_page, self.max_page)
        self.slice()
        self.fetch_thumb()
        return None

    def slice(self) -> None:
        l_start = self.TILE_ITEMS_PER_PAGE * (self.f_page - 1) if self.is_tile \
            else self.ITEMS_PER_PAGE * (self.f_page - 1)
        l_end = l_start + self.TILE_ITEMS_PER_PAGE if self.is_tile else l_start + self.ITEMS_PER_PAGE
        l_end = len(self.f_children) if len(self.f_children) < l_end else l_end
        l_display_items = []
        for i in range(l_start, l_end):
            l_display_items.append(self.f_children[i])
        self.f_children.clear()
        self.f_children.extend(l_display_items)
        return None

    def fetch_thumb(self) -> None:
        for c in self.f_children:
            if 'png' == c.type or 'jpg' == c.type:
                c.fetch_thumb()
        return None


class AbstractDocument(AbstractItem):

    def __init__(self):
        super().__init__()
        self.f_content: str = ''

    @property
    def content(self) -> str:
        return self.f_content

    @staticmethod
    def new(a_id: str, a_type: str, a_name: str, a_describe: bool = False):
        if 'png' == a_type or 'jpg' == a_type:
            l_d = Image()
        elif 'pdf' == a_type:
            l_d = Pdf()
        elif 'txt' == a_type:
            l_d = Text()
        elif 'mp4' == a_type or 'm4a' == a_type or 'mp3' == a_type:
            l_d = Media()
        else:
            l_d = AbstractDocument()
        l_d.id = a_id
        l_d.type = a_type
        l_d.name = a_name
        if a_describe:
            l_d.describe()
        return l_d

    def describe(self) -> DocumentQuery:
        l_dq = DocumentQuery()
        l_dq.id = self.id
        l_d = l_dq.get_document()
        self.type = l_d['type']
        self.name = l_d['fileName']
        self.fill_ancestors(str(l_d['folderId']))
        self.f_content = l_d['fileName']
        return l_dq

    def download_content(self) -> None:
        l_dq = DocumentQuery()
        l_dq.id = self.id
        l_d = l_dq.get_document()
        l_p = os.path.join(BASE_DIR, 'static', l_d['fileName'])
        if os.path.exists(l_p):
            os.remove(l_p)
        l_f = open(l_p, 'wb')
        l_f.write(l_dq.get_content())
        l_f.close()
        return None


class Image(AbstractDocument):

    def __init__(self):
        super().__init__()
        self.f_thumb: str = ''

    @property
    def thumb(self) -> str:
        return self.f_thumb

    def describe(self) -> None:
        l_dq = super().describe()
        self.f_content = 'data:image/jpeg;base64,' + base64.b64encode(l_dq.get_content()).decode()
        return None

    def fetch_thumb(self) -> None:
        l_dq = DocumentQuery()
        l_dq.id = self.id
        self.f_thumb = 'data:image/jpeg;base64,' + base64.b64encode(l_dq.get_thumb()).decode()
        return None

    def create_thumb(self) -> None:
        l_dq = DocumentQuery()
        l_dq.id = self.id
        l_dq.create_thumb()
        return None


class Pdf(AbstractDocument):

    def __init__(self):
        super().__init__()
        self.f_page: int = 0
        self.f_pages: list = []

    @property
    def page(self) -> int:
        return self.f_page

    @property
    def pages(self) -> list:
        return self.f_pages

    def describe(self) -> None:
        l_dq = super().describe()
        l_d = l_dq.get_document()
        self.download_content()
        l_p = os.path.join(BASE_DIR, 'static', l_d['fileName'])
        self.f_page = 1
        self.f_pages = Paginator().create_list(1, 1, 2, self.fetch_pdf_page_count(l_p))
        self.f_content = l_d['fileName']
        return None

    @staticmethod
    def fetch_pdf_page_count(arg: str) -> int:
        l_f = open(arg, 'rb')
        l_page_count: int = PyPDF4.PdfFileReader(l_f).getNumPages()
        l_f.close()
        return l_page_count

    def go_to_page(self, arg: int) -> None:
        l_dq = DocumentQuery()
        l_dq.id = self.id
        l_d = l_dq.get_document()
        self.type = l_d['type']
        self.name = l_d['fileName']
        self.fill_ancestors(str(l_d['folderId']))
        l_p = os.path.join(BASE_DIR, 'static', l_d['fileName'])
        l_max_page = self.fetch_pdf_page_count(l_p)
        arg = 1 if 1 > arg else arg
        arg = l_max_page if l_max_page < arg else arg
        l_prev_page = arg - 1 if 1 < arg else 1
        l_next_page = arg + 1 if l_max_page > arg else l_max_page
        self.f_page = arg
        self.f_pages = Paginator().create_list(arg, l_prev_page, l_next_page, l_max_page)
        self.f_content = l_d['fileName']
        return None


class Text(AbstractDocument):

    def describe(self) -> None:
        l_dq = super().describe()
        self.f_content = l_dq.get_content().decode()
        return None


class Media(AbstractDocument):

    def describe(self) -> None:
        l_dq = super().describe()
        self.download_content()
        self.f_content = l_dq.get_document()['fileName']
        return None


class Paginator:

    def __init__(self):
        self.f_page: int = 0
        self.f_text: str = ''
        self.f_is_current: bool = False
        self.CAPTION_PREV: str = 'Previous'
        self.CAPTION_NEXT: str = 'Next'
        self.CAPTION_DOT: str = '...'

    @property
    def page(self) -> int:
        return self.f_page

    @property
    def text(self) -> str:
        return self.f_text

    @property
    def is_current(self) -> bool:
        return self.f_is_current

    @page.setter
    def page(self, arg: int):
        self.f_page = arg

    @text.setter
    def text(self, arg: str):
        self.f_text = arg

    @is_current.setter
    def is_current(self, arg: bool):
        self.f_is_current = arg

    def create_list(self, current_page: int, prev_page: int, next_page: int, max_page: int) -> list:
        l_pages: list = []
        if 9 > max_page:
            l_pages = self.create_first_2(l_pages, prev_page)
            l_pages = self.create_center(l_pages, 2, max_page)
            l_pages = self.create_last_2(l_pages, next_page, max_page)
            l_pages = self.mark_current(l_pages, current_page)
            return l_pages
        if 1 + 4 > current_page:
            l_pages = self.create_first_2(l_pages, prev_page)
            l_pages = self.create_center(l_pages, 2, current_page + 3)
            l_pages = self.create_next_dot(l_pages, current_page)
            l_pages = self.create_last_2(l_pages, next_page, max_page)
            l_pages = self.mark_current(l_pages, current_page)
            return l_pages
        if max_page - 4 < current_page:
            l_pages = self.create_first_2(l_pages, prev_page)
            l_pages = self.create_prev_dot(l_pages, current_page)
            l_pages = self.create_center(l_pages, current_page - 2, max_page)
            l_pages = self.create_last_2(l_pages, next_page, max_page)
            l_pages = self.mark_current(l_pages, current_page)
            return l_pages
        l_pages = self.create_first_2(l_pages, prev_page)
        l_pages = self.create_prev_dot(l_pages, current_page)
        l_pages = self.create_center(l_pages, current_page - 2, current_page + 3)
        l_pages = self.create_next_dot(l_pages, next_page)
        l_pages = self.create_last_2(l_pages, next_page, max_page)
        l_pages = self.mark_current(l_pages, current_page)
        return l_pages

    def create_first_2(self, pages: list, prev_page: int) -> list:
        l_add = Paginator()
        l_add.page = 1
        l_add.text = '1'
        pages.append(l_add)
        l_add = Paginator()
        l_add.page = prev_page
        l_add.text = self.CAPTION_PREV
        pages.append(l_add)
        return pages

    def create_prev_dot(self, pages: list, current_page: int) -> list:
        l_add = Paginator()
        l_add.page = current_page - 3
        l_add.text = self.CAPTION_DOT
        pages.append(l_add)
        return pages

    @staticmethod
    def create_center(pages: list, start: int, end: int) -> list:
        for p in range(start, end):
            l_add = Paginator()
            l_add.page = p
            l_add.text = str(p)
            pages.append(l_add)
        return pages

    def create_next_dot(self, pages: list, current_page: int) -> list:
        l_add = Paginator()
        l_add.page = current_page + 3
        l_add.text = self.CAPTION_DOT
        pages.append(l_add)
        return pages

    def create_last_2(self, pages: list, next_page: int, max_page: int) -> list:
        l_add = Paginator()
        l_add.page = next_page
        l_add.text = self.CAPTION_NEXT
        pages.append(l_add)
        l_add = Paginator()
        l_add.page = max_page
        l_add.text = str(max_page)
        pages.append(l_add)
        return pages

    @staticmethod
    def mark_current(pages: list, current_page: int) -> list:
        for p in pages:
            if current_page == p.page:
                p.is_current = True
        return pages
