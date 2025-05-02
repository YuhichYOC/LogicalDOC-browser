#
# Query.py
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
import json
import os
import os.path
import stat
import urllib.parse
import urllib.request

import environ
import requests

from browser.settings import BASE_DIR
from com.yoclabo.setting import LogicalDOCServer

env = environ.Env()
env.read_env('.env')

ITEM_TYPE_DIRECTORY = 'directory'

ITEM_TYPE_TEXT = 'text'

ITEM_TYPE_IMAGE = 'image'

ITEM_TYPE_PDF = 'pdf'

ITEM_TYPE_MEDIA = 'media'

ITEM_TYPE_OTHER = 'other'


def resolve_root_id() -> str:
    l_f = FolderQuery()
    l_f.path = '/'
    return str(l_f.find_by_path()['id'])


def query_current_folder_id(id: str) -> str:
    l_d = DocumentQuery()
    l_d.id = id
    return str(l_d.get_document()['folderId'])


def query_ancestors(id: str, type: str, ancestors: list = None) -> list:
    ancestors = []
    l_f = FolderQuery()
    if not id:
        id = resolve_root_id()
    elif type != ITEM_TYPE_DIRECTORY:
        id = query_current_folder_id(id)
    l_f.id = id
    for a in l_f.get_path():
        ancestors.append({'id': str(a['id']), 'type': ITEM_TYPE_DIRECTORY, 'name': a['name']})
    return ancestors


def query_children(id: str) -> list:
    l_children = []
    l_f = FolderQuery()
    if not id:
        id = resolve_root_id()
    l_f.id = id
    for f in l_f.list_children():
        l_children.append({'id': f['id'], 'type': ITEM_TYPE_DIRECTORY, 'name': f['name']})
    for d in l_f.list_document():
        l_children.append({'id': d['id'], 'type': get_type(d['type']), 'name': d['fileName']})
    return l_children


def get_type(type: str) -> str:
    if type == ITEM_TYPE_DIRECTORY:
        return type
    elif type == 'txt':
        return ITEM_TYPE_TEXT
    elif type == 'png' or type == 'jpg':
        return ITEM_TYPE_IMAGE
    elif type == 'pdf':
        return ITEM_TYPE_PDF
    elif type == 'mp4' or type == 'm4a' or type == 'mp3' or type == 'flv' or type == 'wmv':
        return ITEM_TYPE_MEDIA
    return ITEM_TYPE_OTHER


def create_directory(id: str, name: str) -> None:
    l_f = FolderQuery()
    l_f.id = id
    l_f.create_folder(name)
    return


def create_file(id: str, name: str, content: any) -> None:
    l_f = FolderQuery()
    l_f.id = id
    l_f.create_document(env('LOGICALDOC_LANGUAGE'), name, content)
    return


def get_text_content(id: str) -> str:
    l_d = DocumentQuery()
    l_d.id = id
    return l_d.get_content().decode()


def update_text_content(id: str, name: str, content: str) -> None:
    l_d = DocumentQuery()
    l_d.id = id
    l_d.update_content(name, content)
    return


def get_web_encoded_image(id: str) -> str:
    l_d = DocumentQuery()
    l_d.id = id
    return 'data:image/jpeg;base64,' + base64.b64encode(l_d.get_content()).decode()


def get_image_bytearray(id: str) -> bytes:
    l_d = DocumentQuery()
    l_d.id = id
    return l_d.get_content()


def copy_file_to_static(id: str, name: str) -> None:
    l_copy_to = os.path.join(BASE_DIR, 'static', name)
    if os.path.exists(l_copy_to):
        os.remove(l_copy_to)
    l_d = DocumentQuery()
    l_d.id = id
    with open(l_copy_to, 'wb') as f:
        f.write(l_d.get_content())
    os.chmod(l_copy_to, stat.S_IREAD | stat.S_IWRITE | stat.S_IROTH)
    return


class Query:

    def __init__(self):
        self.SERVER: str = LogicalDOCServer.get_logicaldoc_url()
        self.USER: str = LogicalDOCServer.get_logicaldoc_auth_params()['u']
        self.PASSWORD: str = LogicalDOCServer.get_logicaldoc_auth_params()['pw']
        self.f_id: str = ''
        self.f_path: str = ''
        self.f_url: str = ''

    @property
    def id(self) -> str:
        return self.f_id

    @property
    def path(self) -> str:
        return self.f_path

    @property
    def url(self) -> str:
        return self.f_url

    @id.setter
    def id(self, arg: str):
        self.f_id = arg

    @path.setter
    def path(self, arg: str):
        self.f_path = arg

    @url.setter
    def url(self, arg: str):
        self.f_url = arg

    def run(self, mime_type: str) -> bytes:
        l_request = urllib.request.Request(self.SERVER + self.f_url)
        l_request.add_header('Accept', mime_type)
        return self.send_request(l_request)

    def post(self, content_type: str, body: dict) -> bytes:
        l_request = urllib.request.Request(self.SERVER + self.f_url, method='POST')
        l_request.data = json.dumps(body).encode()
        l_request.add_header('Content-Type', content_type)
        return self.send_request(l_request)

    def post_multipart(self, body: dict, url: str) -> requests.Response:
        return requests.post(
            self.SERVER + url,
            files=body,
            headers={'Content-Type': 'multipart/form-data'},
            auth=(self.USER, self.PASSWORD)
        )

    def put(self, mime_type: str) -> bytes:
        l_request = urllib.request.Request(self.SERVER + self.f_url, method='PUT')
        l_request.add_header('Accept', mime_type)
        return self.send_request(l_request)

    def send_request(self, l_request) -> bytes:
        l_request.add_header(
            'Authorization', 'Basic ' + base64.b64encode((self.USER + ':' + self.PASSWORD).encode()).decode()
        )
        with urllib.request.urlopen(l_request) as l_response:
            ret = l_response.read()
        return ret


class FolderQuery(Query):

    def get_folder(self):
        self.url = 'services/rest/folder/getFolder?folderId=' + self.id
        return json.loads(self.run('application/json'))

    def get_path(self):
        self.url = 'services/rest/folder/getPath?folderId=' + self.id
        return json.loads(self.run('application/json'))

    def find_by_path(self):
        self.url = 'services/rest/folder/findByPath?path=' + self.path
        return json.loads(self.run('application/json'))

    def list_children(self):
        self.url = 'services/rest/folder/listChildren?folderId=' + self.id
        return json.loads(self.run('application/json'))

    def list_document(self):
        self.url = 'services/rest/document/listDocuments?folderId=' + self.id
        return json.loads(self.run('application/json'))

    def create_folder(self, folder_name: str) -> None:
        self.url = 'services/rest/folder/create'
        body = {
            'id': self.query_last_folder_id() + 1,
            'name': folder_name,
            'parentId': int(self.id),
        }
        self.post('application/json', body)
        return

    def create_document(self, language: str, file_name: str, content: any) -> None:
        if isinstance(content, str):
            l_file_bytes = content.encode()
            if not file_name.endswith('.txt'):
                file_name += '.txt'
        else:
            l_file_bytes = content.file.read()
        l_file_info = {
            'language': language,
            'fileName': file_name,
            'folderId': int(self.id),
        }
        body = {
            'document': (None, json.dumps(l_file_info), 'application/json'),
            'content': (file_name, l_file_bytes, 'application/octet-stream'),
        }
        ret = self.post_multipart(body, 'services/rest/document/create')
        print(ret)
        return

    def query_last_folder_id(self, folder_id: int = -1) -> int:
        l_q = FolderQuery()
        l_q.path = '/'
        l_q.id = str(l_q.find_by_path()['id'])
        if folder_id == -1:
            l_q.path = '/'
            l_q.id = str(l_q.find_by_path()['id'])
        else:
            l_q.id = str(folder_id)
        ret = int(l_q.id)
        for c in l_q.list_children():
            l_c_last_id = self.query_last_folder_id(c['id'])
            if ret < l_c_last_id:
                ret = l_c_last_id
        return ret


class DocumentQuery(Query):

    def get_document(self):
        self.url = 'services/rest/document/getDocument?docId=' + self.id
        return json.loads(self.run('application/json'))

    def get_content(self) -> bytes:
        self.url = 'services/rest/document/getContent?docId=' + self.id
        return self.run('application/octet-stream')

    def update_content(self, file_name: str, content: any) -> None:
        l_version = self.get_document()['fileVersion'].split('.')
        l_version = ".".join([str(int(l_version[0]) + 1), l_version[1]])
        if isinstance(content, str):
            l_file_bytes = content.encode()
        else:
            l_file_bytes = content.file.read()
        body = {
            'docId': self.id,
            'fileVersion': l_version,
            'filedata': (file_name, l_file_bytes, 'application/octet-stream'),
        }
        l_ret = self.post_multipart(body, 'services/rest/document/replaceFile')
        print(l_ret)
        return

    def get_thumb(self) -> bytes:
        l_q = DocumentQuery()
        l_q.id = self.id
        l_d = l_q.get_document()
        l_q = FolderQuery()
        l_q.id = str(l_d['folderId'])
        l_path_to_dir = ''
        for a in l_q.get_path():
            if a['name'] != '/':
                l_path_to_dir += a['name'] + '/'
        l_arg1 = 'thumb.png'
        l_arg2 = l_path_to_dir
        l_arg3 = l_d['fileName']
        self.url = urllib.parse.quote('services/rest/document/thumbnail/{}/{}{}'.format(l_arg1, l_arg2, l_arg3))
        return self.run('image/png')

    def create_thumb(self) -> None:
        l_q = DocumentQuery()
        l_q.id = self.id
        l_d = l_q.get_document()
        l_arg1 = 'docId=' + self.id
        l_arg2 = 'fileVersion=' + l_d['fileVersion']
        l_arg3 = 'type=thumb.png'
        self.url = urllib.parse.quote('services/rest/document/createThumbnail?{}&{}&{}'.format(l_arg1, l_arg2, l_arg3))
        self.put('application/json')
        return
