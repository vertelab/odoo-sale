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
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import base64
from cStringIO import StringIO

from subprocess import Popen, PIPE
import os
import tempfile
try:
    from xlrd import open_workbook, XLRDError
    from xlrd.book import Book
    from xlrd.sheet import Sheet
except:
    _logger.info('xlrd not installed. sudo pip install xlrd')

from lxml import html
import requests

import re

import logging
_logger = logging.getLogger(__name__)


class SaleOrderImport(models.TransientModel):
    _name = 'sale.order.import.wizard'
    order_file = fields.Binary(string='Order file')
    mime = fields.Selection([('url','url'),('text','text/plain'),('pdf','application/pdf'),('xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),('xls','application/vnd.ms-excel'),('xlm','application/vnd.ms-office')])
    import_customer = fields.Many2one(string='Customer',comodel_name='res.partner')
    info = fields.Text(string='Info')
    tmp_file = fields.Char(string='Tmp File')
    file_name = fields.Char(string='File Name')

    @api.one
    @api.onchange('order_file')
    def check_file(self):
        self.mime = None
        self.import_customer = None
        self.info = None
        self.tmp_file = None

        if self.order_file:
            fd, self.tmp_file = tempfile.mkstemp()
            os.write(fd, base64.b64decode(self.order_file))
            os.close(fd)

            try:
                pop = Popen(['file','-b','--mime',self.tmp_file], shell=False, stdout=PIPE)
                (result, _) = pop.communicate()
                read_mime = result.split(';')[0]
            except OSError,e:
                _logger.warning("Failed attempt to execute file. This program is necessary to check MIME type of %s", fname)
                _logger.debug("Trace of the failed MIME file attempt.", exc_info=True)
                raise Warning(e)

            self.mime = self.get_selection_text('mime',read_mime)

            if self.mime in ['xlsx', 'xls', 'xlm']:
                try:
                    wb = open_workbook(file_contents=base64.b64decode(self.order_file)).sheet_by_index(0)
                except XLRDError, e:
                    raise Warning(e)

                

                if '%s'.lc() % wb.cell_value(0,1) in ('kundnummer','kund','nummer','kundid','customer number','customer'):
                    raise Warning('Hurray')
                    self.import_customer = 'lyko'

            self.info = '%s\n%s' % (self.import_customer,self.get_selection_value('mime',self.mime))


    @api.one
    @api.onchange('order_url')
    def check_url(self):
        self.mime = None
        self.import_customer = None
        self.info = None
        self.tmp_file = None

        if self.order_url:
            self.mime = 'url'
            try:
                page = requests.get(self.order_url.strip())
            except requests.exceptions.RequestException as e:
                raise Warning(e)
            tree = html.fromstring(page.content)
            specter_head = tree.xpath('//tr/td/font/text()')
            specter_lines = tree.xpath('//tr/td/nobr/text()')

            if specter_head and specter_head[6] == 'Naturligt Snygg':
                self.import_customer = 'tailwide'

            self.info = '%s\n%s' % (self.get_selection_value('import_customer',self.import_customer),self.get_selection_value('mime',self.mime))


    @api.multi
    def import_files(self):
        order = None
        missing_products = []
        ordernummer = ''
        orderdatum = ''
        prodnr = re.compile('(\d{4}-\d{5})')

##
##  Excel
##
        if self[0].mime in ['xlsx', 'xls', 'xlm']:
            try:
                wb = open_workbook(file_contents=base64.b64decode(self.order_file)).sheet_by_index(0)
            except XLRDError, e:
                raise ValueError(e)

#
# Lyko
#
            if self[0].import_customer == 'lyko':
                customer = self.env['res.partner'].search([('name','=',self.get_selection_value('import_customer',self.import_customer))])
                order = self.env['sale.order'].create({
                    'partner_id': customer.id,
                    'client_order_ref': wb.cell_value(1,0),
                })
                l = 1
                for line in range(l,wb.nrows):
                    if wb.cell_value(line,4) not in [u'Ert artikelnr', 'Art no', '']:
                        product = self.env['product.product'].search([('default_code','=',wb.cell_value(line,4))])
                        if product:
                            _logger.warn('Rad %s  %s' % (wb.cell_value(line,4),wb.cell_value(line,6)))
                            self.env['sale.order.line'].create({
                                        'order_id': order.id,
                                        'product_id': product.id,
                                        'product_uom_qty': int(wb.cell_value(line,6)),
                                        #'discount': abs(float(wb.cell_value(line,8)))
                                    })
                        else:
                            missing_products.append(wb.cell_value(line,4))

#
# END
#

        if missing_products and order:
            order.note = _('Missing products: ') + ','.join(missing_products)
        if order:
            attachment = self.env['ir.attachment'].create({
                    'name': order.client_order_ref or 'Order'  + '.' + self.mime,
                    'res_name': order.name,
                    'res_model': 'sale.order',
                    'res_id': order.id,
                    'datas': self.order_file,
                    'datas_fname': order.client_order_ref,
                })
            #~ if attachment.mimetype == 'application/pdf':
                #~ attachment.pdf2image(800,1200)

        return {'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_type': 'form',
                'view_mode': 'form',
                 'view_id': self.env.ref('sale.view_order_form').id,
                 'res_id': order.id if order else None,
                 'target': 'current',
                 'context': {},
                 }



    def get_selection_text(self,field,value):
        for type,text in self.fields_get([field])[field]['selection']:
            if text == value:
                return type
        return None

    def get_selection_value(self,field,value):
        for type,text in self.fields_get([field])[field]['selection']:
            if type == value:
                return text
        return None
