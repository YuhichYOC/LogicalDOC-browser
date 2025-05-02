#
# BrowserHandler.py
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
from django.http.response import HttpResponse
from django.shortcuts import render


class BrowserHandler:

    def __init__(self, request: WSGIRequest) -> None:
        self.f_request: WSGIRequest = request
        return

    @property
    def request(self) -> WSGIRequest:
        return self.f_request

    def run(self) -> HttpResponse:
        return render(self.request, 'browser/root.html')
