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
import re
from datetime import datetime
from odoo.addons.sale_showorder_ipf_server.controllers.token import \
    validate_token, valid_response, invalid_response
from odoo.exceptions import ValidationError, UserError

from odoo import http

_logger = logging.getLogger(__name__)


class IpfServer(http.Controller):
    @validate_token
    @http.route("/v1/order", methods=["GET"],
                type="http", auth="none", csrf=False)
    def get_order(self, *args, **kwargs):
        wrong_values = []
        try:
            if kwargs.get('pageNo'):
                int(kwargs.get('pageNo'))
        except:
            message = 'Wrong value pageNo'
            wrong_values.append(message)

        try:
            if kwargs.get('pageSize'):
                int(kwargs.get('pageSize'))
        except:
            message = 'Wrong value pageSize'
            wrong_values.append(message)

        try:
            if kwargs.get('slutDatum'):
                datetime.strptime(kwargs.get('slutDatum'), '%Y-%m-%d')
        except:
            message = 'Wrong value slutDatum'
            wrong_values.append(message)

        try:
            if kwargs.get('startDatum'):
                datetime.strptime(kwargs.get('startDatum'), '%Y-%m-%d')
        except:
            message = 'Wrong value startDatum'
            wrong_values.append(message)

        if kwargs.get('orderstatus') \
                and kwargs.get('orderstatus') not in ["AVBRUTEN", "PRELIMINAR",
                                                      "DEFINITIV", "MAKULERAD",
                                                      "LEVERERAD", "KLAR"]:
            message = 'Wrong value orderstatus'
            wrong_values.append(message)
        if wrong_values:
            message = ',\n'.join(
                missing_value for missing_value in wrong_values)
            return invalid_response("Datafel", message, 400)

        data = [
            {
                "orderId": "MEET-2",
                "utforandeverksamhetNamn": "LOTS-Test10000000",
                "status": "PRELIMINAR",
                "startDatum": "2020-06-01",
                "slutDatum": "2021-01-31",
                "avropsId": "avropsid_23",
                "totalbelopp": "90"
            },
            {
                "orderId": "MEET-1",
                "utforandeverksamhetNamn": "LOTS-Test10000000",
                "status": "PRELIMINAR",
                "startDatum": "2020-06-01",
                "slutDatum": "2021-01-31",
                "avropsId": "avropsid_3",
                "totalbelopp": "90"
            }
        ]
        return valid_response(data)

    @validate_token
    @http.route("/v1/order", methods=["POST"],
                type="http", auth="none", csrf=False)
    def post_order(self, *args, **kwargs):
        values = http.request.httprequest.get_data()
        values_dict = json.loads(values.decode())
        missing_values = []
        result = {
            "ordernummer": "MEET-2"
        }

        return valid_response(result)

    @validate_token
    @http.route("/v1/order/<orderId>", methods=["GET"],
                type="http", auth="none", csrf=False)
    def get_order_id(self, orderId, *args, **kwargs):
        result = {
            "orderId": "MEET-1",
            "bestallare": "bestallaren",
            "tidigareOrderId": None,
            "bokningsId": 127523,
            "definitivDatum": None,
            "lastUpdated": "2020-11-02T15:48:11.256465",
            "orderstatus": "PRELIMINAR",
            "forsakringskassaSamarbete": True,
            "kostnadsstalle": "X75",
            "projektkod": "Projekt 1",
            "avrop": {
                "avropsId": "avropsid_3",
                "startdatum": "2020-10-01",
                "slutdatum": "2020-12-30",
                "diarieaktnummer": "d-334f"
            },
            "avtal": {
                "benamning": "Lots",
                "diarieaktnummer": "AUTO"
            },
            "artikelList": [
                {
                    "id": 2,
                    "tlrId": 166,
                    "namn": "Startersättning",
                    "miaPrisDefinitionTyp": "1",
                    "nuvarandeAntal": 1,
                    "forvantatAntal": 1,
                    "enhet": "2",
                    "nuvarandeAPris": "2000",
                    "forvantatAPris": "2000",
                    "kontokod": "7944",
                    "verksamhetskod": "542601",
                    "finansieringskod": "70227"
                },
                {
                    "id": 1,
                    "tlrId": 167,
                    "namn": "Slutersättning",
                    "miaPrisDefinitionTyp": "1",
                    "nuvarandeAntal": 1,
                    "forvantatAntal": 1,
                    "enhet": "2",
                    "nuvarandeAPris": "7000",
                    "forvantatAPris": "7000",
                    "kontokod": "7944",
                    "verksamhetskod": "542601",
                    "finansieringskod": "70227"
                }
            ],
            "bestallning": {
                "tjanst": {
                    "kod": "A013",
                    "namn": "Karriärvägledning"
                },
                "spar": {
                    "kod": "SP1",
                    "namn": "Spår 1",
                    "sprak": "SE"
                },
                "omfattning": {
                    "startdatum": "2020-06-01",
                    "slutdatum": "2021-01-31",
                    "styck": 0,
                    "anvisningsgrad": 0,
                    "omfattningsgrad": 0
                }
            },
            "beslut": {
                "beslutnummer": 0,
                "uppfoljningskategori": "KVR-V",
                "uppfoljningskategorikod": "U036",
                "startdatum": "2020-10-01",
                "slutdatum": "2020-12-30"
            },
            "leverantor": {
                "konto": "5113-0581",
                "ort": "Lund",
                "postnummer": "22007",
                "fakturaadress": "Box 1067",
                "leverantorsId": "mock",
                "leverantorsNamn": "AB Salgaria",
                "organistationsNummer": "5560401563",
                "utforandeverksamhetNamn": "LOTS-Test10000000",
                "utforande_verksamhet_id": "10000000"
            }
        }
        return valid_response(result)

    @validate_token
    @http.route("/v1/order/<orderNummer>", methods=["PATCH"],
                type="http", auth="none", csrf=False)
    def patch_order(self, orderNummer, *args, **kwargs):
        values = http.request.httprequest.get_data()
        values_dict = json.loads(values.decode())
        return valid_response([])
