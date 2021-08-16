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
import urllib.parse
import urllib.request

import requests

from com.yoclabo.setting import LogicalDOCServer


class Query:

    def __init__(self):
        self.f_server_name: str = LogicalDOCServer.get_logicaldoc_url()
        self.f_auth_id: str = LogicalDOCServer.get_logicaldoc_auth_params()['u']
        self.f_auth_password: str = LogicalDOCServer.get_logicaldoc_auth_params()['pw']
        self.f_id: str = ''
        self.f_path: str = ''
        self.f_url: str = ''

    @property
    def server_name(self) -> str:
        return self.f_server_name

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
        l_request = urllib.request.Request(self.server_name + self.f_url)
        l_request.add_header('Accept', mime_type)
        return self.send_request(l_request)

    def post(self, content_type: str, body: dict) -> bytes:
        l_request = urllib.request.Request(self.server_name + self.f_url, method='POST')
        l_request.data = json.dumps(body).encode()
        l_request.add_header('Content-Type', content_type)
        return self.send_request(l_request)

    def post_multipart(self, body: dict) -> requests.Response:
        return requests.post(self.server_name + self.f_url,
                             files=body,
                             headers={'Content-Type': 'multipart/form-data'},
                             auth=(self.f_auth_id, self.f_auth_password)
                             )

    def put(self, mime_type: str) -> bytes:
        l_request = urllib.request.Request(self.server_name + self.f_url, method='PUT')
        l_request.add_header('Accept', mime_type)
        return self.send_request(l_request)

    def send_request(self, l_request) -> bytes:
        l_request.add_header('Authorization', 'Basic '
                             + base64.b64encode((self.f_auth_id + ':' + self.f_auth_password).encode()).decode())
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
        return None

    def create_document(self, language: str, file_name: str, content) -> None:
        self.url = 'services/rest/document/create'
        l_file_info = {
            'language': language,
            'fileName': file_name,
            'folderId': int(self.id),
        }
        l_file_bytes = content.file.read()
        body = {
            'document': (None, json.dumps(l_file_info), 'application/json'),
            'content': (file_name, l_file_bytes, 'application/octet-stream'),
        }
        self.post_multipart(body)
        return None

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
        return None
