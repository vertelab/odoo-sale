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

import json
import logging
import requests
import uuid
from odoo.tools import pycompat

from odoo import api, http, models, tools, SUPERUSER_ID, fields

_logger = logging.getLogger(__name__)


class ClientConfig(models.Model):
    _name = 'ipf.client.config'
    _description = "IPF Client Config"
    _rec_name = 'url'

    url = fields.Char(string='Url',
                      required=True)
    client_secret = fields.Char(string='Client Secret',
                                required=True)
    client_id = fields.Char(string='Client ID',
                            required=True)
    environment = fields.Selection(selection=[('U1', 'U1'),
                                              ('I1', 'I1'),
                                              ('T1', 'IT'),
                                              ('T2', 'T2'),
                                              ('PROD', 'PROD'), ],
                                   string='Environment',
                                   default='U1',
                                   required=True)
    request_history_ids = fields.One2many('ipf.request.history',
                                          'config_id',
                                          string='Requests')

    def request_call(self, method, url, payload=None,
                     headers=None, params=None):

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

    def create_request_history(self, method, url, response, payload=None,
                               headers=None, params=None):
        values = {'config_id': self.id,
                  'method': method,
                  'url': url,
                  'payload': payload,
                  'request_headers': headers,
                  'response_headers': response.headers,
                  'params': params,
                  'response_code': response.status_code}
        try:
            values.update(message=json.loads(response.content))
        except Exception:
            pass
        self.env['ipf.request.history'].create(values)

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

    def post_data(self):
        querystring = {"client_secret": self.client_secret,
                       "client_id": self.client_id}
        payload = {
            "genomforande_referens": "100000123",
            "utforande_verksamhet_id": "10009858",
            "ordernummer": "MEET-34",
            "tidigare_ordernummer": "MEET-23",
            "boknings_id": "120615",
            "personnummer": "191212121212",
            "sokande_id": "majar8109",
            "tjanstekod": "KVL",
            "spar_kod": "10",
            "sprakstod": "Tyska",
            "deltagandegrad": 75,
            "bokat_sfi": False,
            "startdatum_insats": "2020-01-01",
            "slutdatum_insats": "2020-12-31",
            "startdatum_avrop": "2020-01-01",
            "slutdatum_avrop": "2020-03-31",
            "aktnummer_diariet": "Af-2020/0000 3075",
            "telefonnummer_handlaggargrupp": "+46734176359",
            "epost_handlaggargrupp": "test@test.com"
        }
        url = self.get_url('v1/leverantorsavrop')
        response = self.request_call(method="POST",
                                     url=url,
                                     payload=json.dumps(payload),
                                     headers=self.get_headers(),
                                     params=querystring)

        return response

    @api.model
    def process_data(self, data):
        """For overriding and processing data"""
        return True
