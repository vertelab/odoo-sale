# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit ='res.partner'

    @api.multi
    def name_get(self):
        res = super(ResPartner, self).name_get()
        if not self._context.get('show_contact_type'):
            return res
        types = self._fields['type']
        def find_name(id):
            for t in res:
                if id == t[0]:
                    return t[1].split('\n')[0] #in case show_address_only is active. Anything past the first \n will not be shown in the dropdown
        result = []
        for record in self:
            if record.type and record.type in self.env['ir.config_parameter'].get_param('partner_show_contact_type.types', 'default invoice delivery contact other'):
                result.append((record.id, '%s (%s)' % (find_name(record.id), types.convert_to_export(record.type, self.env))))
            else:
                result.append((record.id, find_name(record.id)))
        _logger.warn(result)
        return result
