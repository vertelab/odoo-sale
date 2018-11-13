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
    from xlrd import open_workbook, XLRDError, XL_CELL_EMPTY,XL_CELL_TEXT,XL_CELL_NUMBER,XL_CELL_DATE,XL_CELL_BOOLEAN,XL_CELL_ERROR,XL_CELL_BLANK    
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
    partner_id = fields.Many2one(string='Customer',comodel_name='res.partner')
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

        def get_value(wb,x,y):
            if wb.cell_type(x, y) == XL_CELL_NUMBER:
                return '%s' % int(wb.cell_value(x, y))
            if wb.cell_type(x, y) == XL_CELL_TEXT:
                return '%s' % wb.cell_value(x, y)
            

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

                
                if '%s'.lower() % wb.cell_value(0,0) in ('kundnummer','kund','nummer','kundid','customer number','customer'):
                    self.partner_id = self.env['res.partner'].search([('ref','=',get_value(wb,0,1))])

            self.info = '%s' % ('Excel formatted file' if self.mime in ['xlsx', 'xls', 'xlm'] else _('Unknown format'))

    @api.multi
    def import_files(self):
        order = None
        missing_products = []
        ordernummer = ''
        orderdatum = ''
        prodnr = re.compile('(\d{4}-\d{5})')

        def get_value(wb,x,y):
            if wb.cell_type(x, y) == XL_CELL_NUMBER:
                return '%s' % int(wb.cell_value(x, y))
            if wb.cell_type(x, y) == XL_CELL_TEXT:
                return '%s' % wb.cell_value(x, y)

##
##  Excel
##
        if self[0].mime in ['xlsx', 'xls', 'xlm']:
            try:
                wb = open_workbook(file_contents=base64.b64decode(self.order_file)).sheet_by_index(0)
            except XLRDError, e:
                raise ValueError(e)

            order = self.env['sale.order'].create({
                'partner_id': self[0].partner_id.id,
                'client_order_ref': get_value(wb,0,3),
            })

            art_col = None
            qty_col = None
            for col in range(0,wb.ncols):
                if get_value(wb.cell_value(1,col)).lower() in [u'ert artikelnr','artikelnr', 'art no','artno','art nr','artnr']:
                    art_col = col
                if get_value(wb.cell_value(1,col)).lower() in [u'antal','qty', 'quantity','ant']:
                    qty_col = col
            
            l = 2
            for line in range(l,wb.nrows):
                if get_value(wb,line,art_col) == '':
                    continue
                if get_value(wb,line,art_col) and len(prodnr.findall(get_value(wb,line,art_col))) > 0:
                    product = self.env['product.product'].search([('default_code','=',prodnr.findall(get_value(wb,line,art_col))[0])])
                    if product:
                        self.env['sale.order.line'].create({
                            'order_id': order.id,
                            'product_id': product.id,
                            'product_uom_qty': wb.cell_value(line,qty_col),
                        })
                    else:
                        missing_products.append(wb.cell_value(line,art_col))

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
