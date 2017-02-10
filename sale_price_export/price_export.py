# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2015 Vertel AB (<http://vertel.se>).
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
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import base64

from tempfile import TemporaryFile

import logging
_logger = logging.getLogger(__name__)

class price_export(models.TransientModel):
    _name = 'price.export'
    _description = 'Products for exports'
    _order = 'name'

    data = fields.Binary('File')
    @api.one
    def _data(self):
        self.xml_file = self.data
    xml_file = fields.Binary(compute='_data')
    name = fields.Char('File Name', readonly=True)
   
    @api.multi
    def send_form(self,):
        account = self[0]
        #_logger.warning('data %s b64 %s ' % (account.data,base64.decodestring(account.data)))
        if not account.data == None:
            fileobj = TemporaryFile('w+')
            fileobj.write(base64.decodestring(account.data))
            fileobj.seek(0)
            try:
                tools.convert_xml_import(account._cr, 'account_export', fileobj, None, 'init', False, None)
            finally:
                fileobj.close()
            return True
        account.write({'state': 'get', 'name': '%s.xml' % account.model.model.replace('.','_'),'data': base64.b64encode(account._export_xml()) })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.export',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': account.id,
            'views': [(False, 'form')],
            'target': 'new',
        }


