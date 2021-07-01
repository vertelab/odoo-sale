# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2018 Vertel AB (<http://vertel.se>).
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
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.tools import float_compare
import logging
import base64
import re

from subprocess import Popen, PIPE
import os
import tempfile

_logger = logging.getLogger(__name__)

try:
    from xlrd import open_workbook, XLRDError, XL_CELL_EMPTY, XL_CELL_TEXT, XL_CELL_NUMBER, XL_CELL_DATE, \
        XL_CELL_BOOLEAN, XL_CELL_ERROR, XL_CELL_BLANK
    from xlrd.book import Book
    from xlrd.sheet import Sheet
except:
    _logger.info('xlrd not installed. sudo pip install xlrd')


class SaleOrderImport(models.TransientModel):
    _name = 'sale.order.import.wizard'

    order_file = fields.Binary(string='Order file')
    mime = fields.Selection([('url', 'url'), ('text', 'text/plain'), ('pdf', 'application/pdf'),
                             ('xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                             ('xls', 'application/vnd.ms-excel'), ('xlm', 'application/vnd.ms-office')])
    partner_id = fields.Many2one(string='Customer', comodel_name='res.partner')
    info = fields.Text(string='Info')
    tmp_file = fields.Char(string='Tmp File')
    file_name = fields.Char(string='File Name')

    @api.onchange('order_file')
    def check_file(self):
        self.mime = None
        self.info = None
        self.tmp_file = None

        def get_value(wb, x, y):
            if wb.cell_type(x, y) == XL_CELL_NUMBER:
                return '%s' % int(wb.cell_value(x, y))
            if wb.cell_type(x, y) == XL_CELL_TEXT:
                return '%s' % wb.cell_value(x, y)

        if self.order_file:
            fd, self.tmp_file = tempfile.mkstemp()
            os.write(fd, base64.b64decode(self.order_file))
            os.close(fd)

            try:
                pop = Popen(['file', '-b', '--mime', self.tmp_file], shell=False, stdout=PIPE)
                result = pop.communicate()[0]
                read_mime = result.split(b';')[0]
            except OSError as e:
                _logger.warning("Failed attempt to execute file. This program is necessary to check MIME type")
                _logger.debug("Trace of the failed MIME file attempt.", exc_info=True)
                raise Warning(e)

            self.mime = self.get_selection_text('mime', read_mime)
            if not self.mime:
                # Guess mime from file name
                self.mime = self.file_name.split('.')[-1]
            
            if self.mime in ['xlsx', 'xls', 'xlm']:
                try:
                    wb = open_workbook(file_contents=base64.b64decode(self.order_file)).sheet_by_index(0)
                except XLRDError as e:
                    raise Warning(e)

                if '%s'.lower() % wb.cell_value(0, 0) in ('kundnummer', 'kund', 'nummer', 'kundid',
                                                         'customer number',  'customer'):
                    self.partner_id = self.env['res.partner'].search([('ref', '=', get_value(wb, 0, 1))])

            self.info = '%s' % ('Excel formatted file' if self.mime in ['xlsx', 'xls', 'xlm'] else _('Unknown format'))

    def import_files(self):
        order = None
        missing_products = []
        out_of_stock = []
        ordernummer = ''
        orderdatum = ''
        prodnr = re.compile('(\d{4}-\d{5})')

        def get_value(wb, x, y):
            if wb.cell_type(x, y) == XL_CELL_NUMBER:
                return '%s' % int(wb.cell_value(x, y))
            if wb.cell_type(x, y) == XL_CELL_TEXT:
                return '%s' % wb.cell_value(x, y)

##
##  Excel
##
        wb = open_workbook(file_contents=base64.b64decode(self.order_file)).sheet_by_index(0)
        partner_id = self.env['res.partner'].search([('ref', '=', get_value(wb, 0, 1))])
        if self[0].mime in ['xlsx', 'xls', 'xlm']:
            try:
                wb = open_workbook(file_contents=base64.b64decode(self.order_file)).sheet_by_index(0)
            except XLRDError as e:
                raise ValueError(e)

            order = self.env['sale.order'].create({
                'partner_id': partner_id.id,
                'client_order_ref': get_value(wb, 0, 3),
                # 'message_follower_ids': [(4, partner_id.id), (3, self.env.user.partner_id.id)],
            })
            res = order.onchange(order.read()[0], 'partner_id', order._onchange_spec())
            if res.get('value'):
                order.write(res['value'])

            art_col = None
            qty_col = None
            for col in range(0, wb.ncols):
                if not art_col:
                    val = get_value(wb, 1, col)
                    if val and val.lower() in [u'ert artikelnr', 'artikelnr', 'art no', 'artno', 'art nr', 'artnr']:
                        art_col = col
                if not qty_col:
                    val = get_value(wb, 1, col)
                    if val and val.lower() in [u'antal', 'qty', 'quantity', 'ant']:
                        qty_col = col
            l = 2
            for line in range(l, wb.nrows):
                art = get_value(wb, line, art_col)
                if art == '':
                    continue
                qty = wb.cell_value(line, qty_col)
                product = None
                if art and len(prodnr.findall(art)) > 0:
                    product = self.env['product.product'].search([('default_code', '=', prodnr.findall(art)[0])])
                    if product:
                        order_line = self.env['sale.order.line'].create({
                            'order_id': order.id,
                            'product_id': product.id,
                            'product_uom_qty': qty,
                        })
                        if product.type == 'product':
                            # determine if the product needs further check for stock availibility
                            # is_available = order_line._check_routing(product, order.warehouse_id.id) and product.sale_ok
                            is_available = product.sale_ok

                            # check if product is available, and if not: raise a warning,
                            # but do this only for products that aren't processed in MTO
                            if not is_available and order_line.product_id.virtual_available_days < 5:
                                _logger.warning('sale_order_import product %s days %s ' %
                                                (order_line.product_id.name,
                                                 order_line.product_id.virtual_available_days))
                                compare_qty = float_compare(order_line.product_id.virtual_available,
                                                            order_line.product_uom_qty,
                                                            precision_rounding=order_line.product_uom.rounding)
                                _logger.warning('sale_order_import product %s compare %s sale_ok %s ' %
                                                (order_line.product_id.name,compare_qty,
                                                 order_line.product_id.sale_ok))
                                if compare_qty == -1 or not product.sale_ok or not product.active or not \
                                        product.website_published:
                                    out_of_stock.append(art)
                if not product:
                    missing_products.append(art)

#
# END

        order.note = _('Imported with Standard Order Import')
        if missing_products and order:
            order.note += _('\nMissing products: ') + ','.join(missing_products)
        
        if out_of_stock and order:
            order.note += _('\nOut of stock: ') + ','.join(out_of_stock)

        if order:
            attachment = self.env['ir.attachment'].create({
                    'name': order.client_order_ref or 'Order' + '.' + self.mime,
                    'res_name': order.name,
                    'res_model': 'sale.order',
                    'res_id': order.id,
                    'datas': self.order_file,
                    'store_fname': order.client_order_ref,
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('sale.view_order_form').id,
            'res_id': order.id if order else None,
            'target': 'current',
            'context': {},
         }

    def get_selection_text(self, field, value):
        for text_type, text in self.fields_get([field])[field]['selection']:
            if text == value:
                return text_type
        return None

    def get_selection_value(self, field, value):
        for text_type, text in self.fields_get([field])[field]['selection']:
            if text_type == value:
                return text
        return None
