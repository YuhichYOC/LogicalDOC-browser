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
        self.f_ancestors: list = []

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

    @id.setter
    def id(self, arg: str):
        self.f_id = arg

    @type.setter
    def type(self, arg: str):
        self.f_type = arg

    @name.setter
    def name(self, arg: str):
        self.f_name = arg

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
        return None


class Folder(Item):

    def __init__(self):
        super().__init__()
        self.f_sub_folders: list = []
        self.f_sub_documents: list = []

    @property
    def sub_folders(self) -> list:
        return self.f_sub_folders

    @property
    def sub_documents(self) -> list:
        return self.f_sub_documents

    def describe_root_folder(self) -> None:
        l_q = Query.FolderQuery()
        l_q.path = '/'
        self.id = str(l_q.find_by_path()['id'])
        self.describe()
        return None

    def describe(self) -> None:
        l_q = Query.FolderQuery()
        l_q.id = self.id
        self.name = l_q.get_folder()['name']
        self.f_sub_folders.clear()
        for f in l_q.list_children():
            add = Folder()
            add.id = str(f['id'])
            add.type = 'folder'
            add.name = f['name']
            self.f_sub_folders.append(add)
        self.f_sub_documents.clear()
        for d in l_q.list_document():
            add = Document()
            add.id = str(d['id'])
            add.type = d['type']
            add.name = d['fileName']
            add.fetch_thumb()
            self.f_sub_documents.append(add)
        self.fill_ancestors(self.id)
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
        if self.type != 'png' and self.type != 'jpg':
            return None
        l_q = Query.DocumentQuery()
        l_q.id = self.id
        self.f_thumb = 'data:image/jpeg;base64,' + base64.b64encode(l_q.get_thumb()).decode()
        return None

    def create_thumb(self) -> None:
        if self.type != 'png' and self.type != 'jpg':
            return None
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
        if self.type != 'png' and self.type != 'jpg':
            return None
        self.f_image = 'data:image/jpeg;base64,' + base64.b64encode(l_q.get_content()).decode()
        return None
