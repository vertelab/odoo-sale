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

import logging
import json
from odoo.exceptions import ValidationError, UserError
from odoo import http
from datetime import datetime
from odoo.addons.sale_suborder_ipf_server.controllers.token import \
    validate_token, valid_response, invalid_response
import re
from odoo.http import request
_logger = logging.getLogger(__name__)


class IpfServer(http.Controller):

    @validate_token
    @http.route("/v1/leverantorsavrop", methods=["POST"],
                type="http", auth="none", csrf=False)
    def leverantorsavrop(self, *args, **kwargs):
        required_keys = ["genomforande_referens",
                         "utforande_verksamhet_id",
                         "ordernummer",
                         "boknings_id",
                         "personnummer",
                         "sokande_id",
                         "tjanstekod",
                         "deltagandegrad",
                         "startdatum_insats",
                         "slutdatum_insats",
                         "slutdatum_avrop",
                         "aktnummer_diariet",
                         "telefonnummer_handlaggargrupp",
                         "epost_handlaggargrupp"]

        values = http.request.httprequest.get_data()
        values_dict = json.loads(values.decode())
        missing_values = []

        for required_key in required_keys:
            print('values_dict.get(required_key) >>>>>', values_dict.get(required_key))
            if not values_dict.get(required_key):
                missing_values.append(required_key)
        if missing_values:
            message = 'The keys {} is required'.format(
                ','.join(missing_value for missing_value in missing_values))
            return invalid_response("Datafel", message, 400)

        wrong_values = []
        pattern = re.compile("^\\d{12}$")
        if not pattern.match(values_dict.get('personnummer')):

            message = 'Wrong value personnummer'
            wrong_values.append(message)

        pattern = re.compile("^.+@.+\\..+$")
        if not pattern.match(values_dict.get('epost_handlaggargrupp')):
            message = 'Wrong value epost_handlaggargrupp'
            wrong_values.append(message)

        try:
            deltagandegrad = int(values_dict.get('deltagandegrad'))
            if 50 >= deltagandegrad >= 100:
                message = 'The value deltagandegrad is out of range [50, 100]'
                wrong_values.append(message)

        except ValidationError as e:
            return invalid_response("Internal Server Error", e, 500)

        startdatum_insats = values_dict.get('startdatum_insats')
        try:
            datetime.strptime(startdatum_insats, '%Y-%m-%d')
        except:
            message = 'Wrong value startdatum_insats'
            wrong_values.append(message)

        slutdatum_insats = values_dict.get('slutdatum_insats')
        try:
            datetime.strptime(slutdatum_insats, '%Y-%m-%d')
        except:
            message = 'Wrong value slutdatum_insats'
            wrong_values.append(message)

        startdatum_avrop = values_dict.get('startdatum_avrop')
        try:
            datetime.strptime(startdatum_avrop, '%Y-%m-%d')
        except:
            message = 'Wrong value startdatum_avrop'
            wrong_values.append(message)

        slutdatum_avrop = values_dict.get('slutdatum_avrop')
        try:
            datetime.strptime(slutdatum_avrop, '%Y-%m-%d')
        except:
            message = 'Wrong value slutdatum_avrop'
            wrong_values.append(message)

        if wrong_values:
            message = ',\n'.join(wrong_value for wrong_value in wrong_values)
            return invalid_response("Datafel", message, 400)
        return valid_response([])
