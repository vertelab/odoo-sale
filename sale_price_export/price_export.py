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

try:
    import unicodecsv as csv
except:
    _logger.warn('sale_price_export requires unicodecsv (sudo pip install unicodecsv)')

class price_export(models.TransientModel):
    _name = 'price.export'
    _description = 'Products for exports'
    _order = 'name'

    data = fields.Binary('File')
    csv_file = fields.Binary(compute='_get_csv_file')
    name = fields.Char('File Name', readonly=True)
    price_version_id = fields.Many2one(comodel_name='product.pricelist.version', string='Pricelist')
    
    @api.one
    @api.onchange('price_version_id')
    def _get_csv_file(self):
        with TemporaryFile('w+') as fileobj:
            writer = csv.DictWriter(fileobj, fieldnames=['product_id', 'product_name', 'price'])
            writer.writeheader()
            for product in self.env['product.product'].search([]):
                item = None
                if self.price_version_id:
                    item = self.env['product.pricelist.item'].search([('product_id', '=', product.id), ('price_version_id', '=', self.price_version_id.id)])
                writer.writerow({
                    'product_id': product.id,
                    'product_name': product.display_name,
                    'price': item and item.price_surcharge or product.lst_price,
                })
            self.csv_file = fileobj
    
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
            'res_model': 'price.export',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': account.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
    
    def create_csv(self):
        products = env['product.product'].search([])
for list in env['product.pricelist.version'].browse(context.get('active_ids', [])):
    for product in products:
        if not env['product.pricelist.item'].search_count([('product_id', '=', product.id), ('price_version_id', '=', list.id)]):
            list.items_id |= env['product.pricelist.item'].create(
            {
                'product_id': product.id,
                'sequence': 3,
                'base': 1,
                'price_discount': -1,
                'price_surcharge': product.lst_price,
            }
            )
    
    def import_file(self):
        pass


