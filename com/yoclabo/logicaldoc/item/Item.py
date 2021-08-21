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

from com.yoclabo.logicaldoc.query import Query


class Item:

    def __init__(self):
        self.f_id: str = ''
        self.f_type: str = ''
        self.f_name: str = ''
        self.f_sequence: int = 0
        self.f_ancestors: list = []
        self.f_pages: list = []

    @property
    def id(self) -> str:
        return self.f_id

    @property
    def type(self) -> str:
        return self.f_type

    @property
    def is_folder(self) -> bool:
        if self.type == 'folder':
            return True
        return False

    @property
    def is_image(self) -> bool:
        if self.type == 'png':
            return True
        if self.type == 'jpg':
            return True
        return False

    @property
    def name(self) -> str:
        return self.f_name

    @property
    def sequence(self) -> int:
        return self.f_sequence

    @property
    def is_even_row(self) -> bool:
        return True if 0 == self.f_sequence % 2 else False

    @property
    def ancestors(self) -> list:
        return self.f_ancestors

    @property
    def ancestors_count(self) -> int:
        return len(self.f_ancestors)

    @property
    def pages(self) -> list:
        return self.f_pages

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
        l_f = Query.FolderQuery()
        l_f.id = folder_id
        for a in l_f.get_path():
            add = Folder()
            add.id = str(a['id'])
            add.type = 'folder'
            add.name = a['name']
            self.f_ancestors.append(add)
        if self.is_folder:
            del self.f_ancestors[-1]
        return None


class Folder(Item):

    def __init__(self):
        super().__init__()
        self.f_items: list = []
        self.f_items_total: int = 0
        self.f_current_page: int = 0
        self.f_display_items: list = []
        self.ITEMS_PER_PAGE: int = 10

    @property
    def max_page(self) -> int:
        if 0 == self.f_items_total:
            return 1
        # Round up "f_items_total" divided by "ITEMS_PER_PAGE" to get the maximum number of pages.
        return -(-self.f_items_total // self.ITEMS_PER_PAGE)

    @property
    def prev_page(self) -> int:
        return self.f_current_page - 1 if 1 < self.f_current_page else 1

    @property
    def next_page(self) -> int:
        return self.f_current_page + 1 if self.max_page > self.f_current_page else self.max_page

    @property
    def display_items(self) -> list:
        return self.f_display_items

    def describe_root_folder(self) -> None:
        l_q = Query.FolderQuery()
        l_q.path = '/'
        self.id = str(l_q.find_by_path()['id'])
        self.describe()
        return None

    def describe(self) -> None:
        self.f_items.clear()
        l_q = Query.FolderQuery()
        l_q.id = self.id
        self.name = l_q.get_folder()['name']
        for f in l_q.list_children():
            add = Folder()
            add.id = str(f['id'])
            add.type = 'folder'
            add.name = f['name']
            add.sequence = len(self.f_items) + 1
            self.f_items.append(add)
        for d in l_q.list_document():
            add = Document()
            add.id = str(d['id'])
            add.type = d['type']
            add.name = d['fileName']
            add.sequence = len(self.f_items) + 1
            self.f_items.append(add)
        self.f_items_total = len(self.f_items)
        self.f_current_page = 1
        self.f_pages = Page(0, '').create_list(self.f_current_page, self.prev_page, self.next_page, self.max_page)
        self.fill_ancestors(self.id)
        return None

    def go_to_page(self, arg: int) -> None:
        self.f_current_page = arg
        if 1 > self.f_current_page:
            self.f_current_page = 1
        if self.max_page < self.f_current_page:
            self.f_current_page = self.max_page
        self.f_pages = Page(0, '').create_list(self.f_current_page, self.prev_page, self.next_page, self.max_page)
        self.fetch_thumb()
        return None

    def fetch_thumb(self) -> None:
        l_start = self.ITEMS_PER_PAGE * (self.f_current_page - 1)
        l_end = l_start + self.ITEMS_PER_PAGE
        if self.f_items_total < l_end:
            l_end = self.f_items_total
        self.f_display_items.clear()
        for i in range(l_start, l_end):
            if self.f_items[i].is_image:
                self.f_items[i].fetch_thumb()
            self.f_display_items.append(self.f_items[i])
        return None


class Document(Item):

    def __init__(self):
        super().__init__()
        self.f_thumb: str = ''
        self.f_content: str = ''
        self.f_image: str = ''

    @property
    def thumb(self) -> str:
        return self.f_thumb

    @property
    def content(self) -> str:
        return self.f_content

    @property
    def image(self) -> str:
        return self.f_image

    def fetch_thumb(self) -> None:
        l_q = Query.DocumentQuery()
        l_q.id = self.id
        self.f_thumb = 'data:image/jpeg;base64,' + base64.b64encode(l_q.get_thumb()).decode()
        return None

    def create_thumb(self) -> None:
        l_q = Query.DocumentQuery()
        l_q.id = self.id
        l_q.create_thumb()
        return None

    def describe(self) -> None:
        l_q = Query.DocumentQuery()
        l_q.id = self.id
        l_d = l_q.get_document()
        self.type = l_d['type']
        self.name = l_d['fileName']
        self.fill_ancestors(str(l_d['folderId']))
        if self.is_image:
            self.f_image = 'data:image/jpeg;base64,' + base64.b64encode(l_q.get_content()).decode()
        return None


class Page:

    def __init__(self, p: int, t: str):
        self.f_page: int = p
        self.f_text: str = t
        self.f_is_current: bool = False
        self.CAPTION_PREV_PAGE: str = 'Previous'
        self.CAPTION_NEXT_PAGE: str = 'Next'
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
        l_pages = self.create_next_dot(l_pages, current_page)
        l_pages = self.create_last_2(l_pages, next_page, max_page)
        l_pages = self.mark_current(l_pages, current_page)
        return l_pages

    def create_first_2(self, l_pages: list, prev_page: int) -> list:
        l_pages.append(Page(1, '1'))
        l_pages.append(Page(prev_page, self.CAPTION_PREV_PAGE))
        return l_pages

    def create_prev_dot(self, l_pages: list, current_page: int) -> list:
        l_pages.append(Page(current_page - 3, self.CAPTION_DOT))
        return l_pages

    @staticmethod
    def create_center(l_pages: list, start: int, end: int) -> list:
        for p in range(start, end):
            l_pages.append(Page(p, str(p)))
        return l_pages

    def create_next_dot(self, l_pages: list, current_page: int) -> list:
        l_pages.append(Page(current_page + 3, self.CAPTION_DOT))
        return l_pages

    def create_last_2(self, l_pages: list, next_page: int, max_page: int) -> list:
        l_pages.append(Page(next_page, self.CAPTION_NEXT_PAGE))
        l_pages.append(Page(max_page, str(max_page)))
        return l_pages

    @staticmethod
    def mark_current(l_pages: list, current_page: int) -> list:
        for p in l_pages:
            if current_page == p.page:
                p.is_current = True
        return l_pages
