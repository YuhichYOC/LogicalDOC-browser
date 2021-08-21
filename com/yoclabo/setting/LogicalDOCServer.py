#
# LogicalDOCServer.py
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

def get_logicaldoc_server_addr() -> str:
    return ''


def get_logicaldoc_server_port() -> str:
    return ''


def get_logicaldoc_server_tenant() -> str:
    return 'logicaldoc'


def get_logicaldoc_server_name() -> str:
    return get_logicaldoc_server_addr() \
           + ':' + get_logicaldoc_server_port() \
           + '/' + get_logicaldoc_server_tenant() + '/'


def get_logicaldoc_url() -> str:
    return 'http://' + get_logicaldoc_server_name()


def get_logicaldoc_auth_params() -> dict:
    return {
        'u': '',
        'pw': '',
    }
