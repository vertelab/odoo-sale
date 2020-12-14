# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

from odoo.tools import pycompat
import json
import uuid
import logging
import requests
from odoo import api, http, models, tools, SUPERUSER_ID, fields

_logger = logging.getLogger(__name__)


class ClientConfig(models.Model):
    _name = 'ipf.showorder.client.config'
    _rec_name = 'url'

    url = fields.Char(string='Url',
                      required=True)
    client_secret = fields.Char(string='Client Secret',
                                required=True)
    client_id = fields.Char(string='Client ID',
                            required=True)
    environment = fields.Selection(selection=[('u1', 'U1'),
                                              ('i1', 'I1'),
                                              ('t1', 'IT'),
                                              ('t2', 'T2'),
                                              ('prod', 'PROD'), ],
                                   string='Environment',
                                   default='u1',
                                   required=True)
    request_history_ids = fields.One2many('ipf.showorder.request.history',
                                          'config_id',
                                          string='Requests')

    def request_call(self, method, url, payload=False,
                     headers=False, params=False):

        response = requests.request(method=method,
                                    url=url,
                                    data=payload,
                                    headers=headers,
                                    params=params)

        self.create_request_history(method=method,
                                    url=url,
                                    response=response,
                                    payload=payload,
                                    headers=headers,
                                    params=params)

        return response

    def create_request_history(self, method, url, response, payload=False,
                               headers=False, params=False):
        values = {'config_id': self.id,
                  'method': method,
                  'url': url,
                  'payload': payload,
                  'request_headers': headers,
                  'response_headers': response.headers,
                  'params': params,
                  'response_code': response.status_code}
        values.update(message=json.loads(response.content))
        self.env['ipf.showorder.request.history'].create(values)

    def get_headers(self):
        tracking_id = pycompat.text_type(uuid.uuid1())
        headers = {
            'x-amf-mediaType': "application/json",
            'AF-TrackingId': tracking_id,
            'AF-SystemId': "AF-SystemId",
            'AF-EndUserId': "AF-EndUserId",
            'AF-Environment': self.environment,
        }
        return headers

    def get_url(self, path):
        if self.url[-1] == '/':
            url = self.url + path
        else:
            url = self.url + '/' + path
        return url

    def get_order(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id,
                       'pageNo': 1,
                       'pageSize': 25,
                       # 'slutDatum': 1,
                       'orderstatus': 'MAKULERAD',
                       # 'startDatum': 1,
                       'avtalsId': 1}

        url = self.get_url('v1/order')
        response = self.request_call(method="GET",
                                     url=url,
                                     headers=self.get_headers(),
                                     params=querystring)

        print(response.text)

    def post_order(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {
            "avrop": {
                "avropsId": "avropsid_1",
                "diarieaktnummer": "d-334f",
                "slutdatum": "2020-12-30",
                "startdatum": "2020-10-01"
            },
            "beslut": {
                "beslutnummer": 0,
                "slutdatum": "2020-12-30",
                "startdatum": "2020-10-01",
                "uppfoljningskategori": "KVR-V",
                "uppfoljningskategorikod": "U036"
            },
            "bestallare": "bestallaren",
            "bestallning": {
                "omfattning": {
                    "anvisningsgrad": 0,
                    "omfattningsgrad": 0,
                    "slutdatum": "2021-01-31",
                    "startdatum": "2020-06-01",
                    "styck": 0
                },
                "spar": {
                    "kod": "SP1",
                    "namn": "Spår 1",
                    "sprak": "SE"
                },
                "tjanst": {
                    "kod": "A013",
                    "namn": "Karriärvägledning"
                }
            },
            "bokningsId": 127523,
            "forsakringskassaSamarbete": True,
            "kontering": {
                "kostnadsstalle": "X75",
                "projektkod": "Projekt 1"
            },
            "leverantor": {
                "utforande_verksamhet_id": "A-10000000"
            }
        }

        url = self.get_url('v1/order')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)

    def get_order_id(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        url = self.get_url('v1/order/%s' % ('order_id_1'))
        response = self.request_call(method="GET",
                                     url=url,
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)

    def patch_order(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {"status": "DEFINITIV"}
        url = self.get_url('v1/order/%s' % ('order_id_1'))
        response = self.request_call(method="PATCH",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)
        print(response.text)
