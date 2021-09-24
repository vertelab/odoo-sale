# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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
import base64
from subprocess import Popen, PIPE
import os
import tempfile
import logging
from lxml import html
import requests
import re

_logger = logging.getLogger(__name__)

try:
    from xlrd import open_workbook, XLRDError
    from xlrd.book import Book
    from xlrd.sheet import Sheet
except:
    _logger.info('xlrd not installed. sudo pip install xlrd')

try:
    import unicodecsv as csv
except:
    _logger.info('Missing unicodecsv. sudo pip install unicodecsv')


class DermanordImport(models.TransientModel):
    _name = 'sale.dermanord.import.wizard'

    order_file = fields.Binary(string='Order file')
    order_url = fields.Char(string='Url')
    mime = fields.Selection([('url', 'url'), ('text', 'text/plain'), ('pdf', 'application/pdf'),
                             ('xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                             ('xls', 'application/vnd.ms-excel'), ('xlm', 'application/vnd.ms-office')])
    import_type = fields.Selection([('bangerhead', 'Bangerhead AB'), ('ahlens', 'Åhléns AB'),
                                    ('tailwide', 'Tailwide AB'), ('harmoniq', 'HARMONIQ AB'),
                                    ('birka', 'BIRKA CRUISES AB'), ('nordicfeel', 'Nordic Web Trading AB'),
                                    ('isaksen', 'Isaksen & CO AS'), ('lyko', 'Lyko Online AB'),
                                    ('finamig', 'Fina mig i Hedemora AB'), ('skincity', 'Skincity Sweden'),
                                    ('skincity_xl', 'Skincity Sweden')])
    info = fields.Text(string='Info')
    tmp_file = fields.Char(string='Tmp File')
    file_name = fields.Char(string='File Name')

    @api.onchange('order_file')
    def check_file(self):
        self.mime = None
        self.import_type = None
        self.info = None
        self.tmp_file = None

        if self.order_file:
            fd, self.tmp_file = tempfile.mkstemp()
            os.write(fd, base64.b64decode(self.order_file))
            os.close(fd)

            try:
                pop = Popen(['file', '-b', '--mime', self.tmp_file], shell=False, stdout=PIPE)
                (result, _) = pop.communicate()
                read_mime = result.split(b';')[0]
            except OSError as e:
                # _logger.warning("Failed attempt to execute file. This program is necessary to check MIME type of %s", fname)
                _logger.warning("Failed attempt to execute file. This program is necessary to check MIME type")
                _logger.debug("Trace of the failed MIME file attempt.", exc_info=True)
                raise Warning(e)

            self.mime = self.get_selection_text('mime',read_mime)

            if self.mime == 'pdf':
                try:
                    pop = Popen(['pdftotext', '-enc', 'UTF-8', '-nopgbrk', self.tmp_file, '-'], shell=False, stdout=PIPE)
                    (content, _) = pop.communicate()
                except OSError as e:
                    _logger.warning("Failed attempt to execute pdftotext. This program is necessary to index the file "
                                    "%s of MIME type %s. Detailed error available at DEBUG level.",
                                    self.tmp_file, self.mime)
                    _logger.debug("Trace of the failed file indexing attempt.", exc_info=True)
                    raise Warning(e)
                lines = content.splitlines()
                if len(lines) >= 19 and lines[19] == 'Fina mig i Hedemora AB':
                    self.import_type = 'finamig'
                elif b'SKINCITY SWEDEN AB' in content:
                    self.import_type = 'skincity'
            elif self.mime in ['xlsx', 'xls', 'xlm']:
                try:
                    wb = open_workbook(file_contents=base64.b64decode(self.order_file)).sheet_by_index(0)
                except XLRDError as e:
                    raise Warning(e)

                if wb.cell_value(0, 2) in (u'Lyko Artikelnr', u'Lyko Art no'):
                    self.import_type = 'lyko'
                if wb.cell_value(0, 0) == u'Isaksen & CO AS ':
                    self.import_type = 'isaksen'
                if wb.cell_value(2, 1) == 13610404.0:
                    self.import_type = 'nordicfeel'
                if wb.cell_value(0, 0) == 'Art nb' and wb.cell_value(0, 2) == 'Colour' and wb.cell_value(0, 3) == 'Size':
                    self.import_type = 'skincity_xl'
                if wb.cell_value(1, 2) == u'Art nr lev' and wb.cell_value(1, 6) == 'Antal':
                    self.import_type = 'bangerhead'

            elif self.mime == 'text':
                birka = re.compile(u'(Rederi Ab Eckerö)')
                if len(birka.findall(self.order_file.decode('base64')))>0:
                    self.import_type = 'birka'

            self.info = '%s\n%s' % (self.get_selection_value('import_type', self.import_type),
                                    self.get_selection_value('mime', self.mime))

    @api.onchange('order_url')
    def check_url(self):
        self.mime = None
        self.import_type = None
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
            ahlens_head = tree.xpath('//div[@class="ramdata"]/text()') # /div[@"ramdata"]
            # ~ raise Warning(ahlens_head)
            specter_lines = tree.xpath('//tr/td/nobr/text()')
            ahlens_lines = tree.xpath('//table/tr')
            # ~ raise Warning(ahlens_lines)

            if specter_head and specter_head[6] == 'Naturligt Snygg':
                self.import_type = 'tailwide'
                
            if specter_head and specter_head[6] == 'HARMONIQ AB':
                self.import_type = 'harmoniq'
            
            # ~ ahlens_heads = []
            # ~ if ahlens_head:
                # ~ ahlens_heads.append(ahlens_head)
                # ~ for ahlens_head in ahlens_heads:
            if u'Åhléns AB' in ''.join(ahlens_head):
                self.import_type = 'ahlens'

            self.info = '%s\n%s' % (self.get_selection_value('import_type', self.import_type),
                                    self.get_selection_value('mime', self.mime))

    def import_files(self):
        def create_order(values):
            order = self.env['sale.order'].create(values)
            res = order.onchange(order.read()[0], 'partner_id', order._onchange_spec())
            if res.get('value'):
                order.write(res['value'])
            return order
        
        order = None
        orders = []
        missing_products = []
        ordernummer = ''
        orderdatum = ''
        prodnr = re.compile('(\d{4}-\d{5})')
        if self[0].mime == 'pdf':
            try:
                #~ pop = Popen(['pdftotext', '-enc', 'UTF-8', '-nopgbrk', fname, '-'], shell=False, stdout=PIPE)
                pop = Popen(['pdf2txt.py', self.tmp_file], shell=False, stdout=PIPE)
                (content, _) = pop.communicate()
            except OSError as e:
                _logger.warning("Failed attempt to execute pdf2txt.py. This program is necessary to decode the file %s "
                                "of MIME type %s. Detailed error available at DEBUG level.", self.tmp_file, self.mime)
                _logger.debug("Trace of the failed file indexing attempt.", exc_info=True)
                raise Warning(e)
            lines = content.splitlines()
            
            

#
#   Fina mig i Hedemora AB
#
            if self[0].import_type == 'finamig':
                customer = self.env['res.partner'].search([('name', '=', self.get_selection_value('import_type',
                                                                                                  self.import_type))])
                artnr = []
                antal = []
                #~ raise Warning(lines)
                for line in range(0, len(lines)):
                    _logger.warn('Line %s|' % lines[line])
                    if lines[line] == 'Art. Nr':
                        line += 1
                        for art in range(line,len(lines)):
                            if lines[art] == '':
                                line = art
                                break
                            _logger.warn('Art Nr %s' % lines[art])
                            artnr.append(lines[art].replace(b'(cid:160)', b''))
                    if lines[line] == 'Antal':
                        for ant in range(line+1,len(lines)):
                            if lines[ant] == '':
                                line = ant
                                break
                            _logger.warn('Antal %s' % lines[ant])
                            antal.append(int(lines[ant].replace(b' st', b'')))
                    if lines[line] == 'Ordernummer':
                        line += 1
                        ordernummer = lines[line]
                    if lines[line] == 'Orderdatum':
                        line += 1
                        orderdatum = lines[line]
                    line += 1
                order = create_order({
                    'partner_id': customer.id,
                    'client_order_ref': ordernummer,
                    'date_order': orderdatum,
                })
                for i, art in enumerate(artnr):
                    product = self.env['product.product'].search([('default_code', '=', art)])
                    if product:
                        self.env['sale.order.line'].create({
                            'order_id': order.id,
                            'product_id': product.id,
                            'product_uom_qty': antal[i] if i < len(antal) else 0,
                        })
                    else:
                        missing_products.append(art)

#
#    Skincity
#
            elif self[0].import_type == 'skincity':
                customer = self.env['res.partner'].search([('name', '=', self.get_selection_value('import_type',
                                                                                                  self.import_type))])
                artnr = []
                antal = []
                _logger.warn('content %s|' % lines)
                for line in range(0, len(lines)):
                    _logger.warning('Line %s|' % lines[line])
                    if lines[line] == 'Beskrivning':
                        line += 1
                        for art in range(line,len(lines)):
                            if lines[art] == '':
                                line = art
                                break
                            if lines[art] == 'gram':
                                continue
                            _logger.warning('Art Nr %s' % lines[art].split()[0])
                            artnr.append(lines[art].split()[0])
                    if lines[line] == 'Antal':
                        for ant in range(line+1,len(artnr)+line+1):
                            _logger.warn('Antal %s | %s (%s)' % (lines[ant],line,len(lines)))
                            if lines[ant] in ['Belopp','Pris / st','Dermanord-Svensk Hudv\xc3\xa5rd AB','Rabatt','Nr.']:
                                break
                            try:
                                antal.append(int(lines[ant].decode('utf-8').replace(u'\xa0', u'') or 0))
                            except Exception as e:
                                raise Warning(e)
                            line += 1
                        _logger.warn('After antal %s | %s %s %s' % (antal,line,len(antal),len(lines)))
                    if lines[line] == 'Inköpsorder':
                        ordernummer = lines[line].split()[1]
                    if lines[line] == 'Orderdatum':
                        orderdatum = lines[line+5]
                    line += 1
                order = create_order({
                    'partner_id': customer.id,
                    'client_order_ref': ordernummer,
                    'date_order': orderdatum,
                })
                #~ _logger.warn('SKINCITY ARTNR %s' % artnr)
                #~ _logger.warn('SKINCITY ANTAL %s' % antal)
                ai = 0
                for i,art in enumerate(artnr):
                    _logger.warn('products: %s %s %s (%s)' % (i,art,ai,len(antal)))
                    if ai <= len(antal):
                        if antal[ai] == 0:
                            ai += 1
                    if len(prodnr.findall(art)) > 0:
                        product = self.env['product.product'].search([('default_code','=',prodnr.findall(art)[0])])
                        if product:
                            self.env['sale.order.line'].create({
                                'order_id': order.id,
                                'product_id': product.id,
                                'product_uom_qty': antal[ai] if len(antal) > ai else 9.9,
                            })
                        else:
                            missing_products.append(art)
                    ai += 1
##
##  Excel
##
        elif self[0].mime in ['xlsx', 'xls', 'xlm']:
            try:
                wb = open_workbook(file_contents=base64.b64decode(self.order_file)).sheet_by_index(0)
            except XLRDError as e:
                raise ValueError(e)

#
# Lyko
#
            if self[0].import_type == 'lyko':
                customer = self.env['res.partner'].search([('name','=',self.get_selection_value('import_type', self.import_type))])
                order = create_order({
                    'partner_id': customer.id,
                    'client_order_ref': wb.cell_value(1,0),
                })
                l = 1
                for line in range(l, wb.nrows):
                    if wb.cell_value(line, 4) not in [u'Ert artikelnr', 'Art no', '']:
                        product = self.env['product.product'].search([('default_code','=', wb.cell_value(line,4))])
                        if product:
                            _logger.warn('Rad %s  %s' % (wb.cell_value(line, 4), wb.cell_value(line,6)))
                            self.env['sale.order.line'].create({
                                        'order_id': order.id,
                                        'product_id': product.id,
                                        'product_uom_qty': int(wb.cell_value(line,6)),
                                        #'discount': abs(float(wb.cell_value(line,8)))
                                    })
                        else:
                            missing_products.append(wb.cell_value(line,4))
#
# Isaksen
#
            if self[0].import_type == 'isaksen':
                #~ customer = self.env['res.partner'].search([('name','=',self.get_selection_value('import_type',self.import_type)),('is_company','=',True)])
                customer = self.env['res.partner'].search([('customer_no', '=', '515'), ('is_company', '=', True), ('customer', '=', True)])
                order = create_order({
                    'partner_id': customer.id,
                    'client_order_ref': int(float('%s%s' % (wb.cell_value(1,8),wb.cell_value(1,9)))),
                })
                l = 18
                for line in range(l,wb.nrows):
                    if wb.cell_value(line,0) not in [u'Item#','']:
                        product = self.env['product.product'].search([('default_code','=',wb.cell_value(line,0))])
                        if product:
                            _logger.warn('Rad %s  %s' % (wb.cell_value(line,0),wb.cell_value(line,5)))
                            self.env['sale.order.line'].create({
                                        'order_id': order.id,
                                        'product_id': product.id,
                                        'product_uom_qty': float('%s%s' % (wb.cell_value(line,5),wb.cell_value(line,6))),
                                    })
                        else:
                            missing_products.append(wb.cell_value(line,0))
#
# Nordic Feel
#
            if self[0].import_type == 'nordicfeel':
                customer = self.env['res.partner'].search([('name','=',self.get_selection_value('import_type',self.import_type))])
                order = create_order({
                    'partner_id': customer.id,
                    'client_order_ref': str(int(wb.cell_value(2,0))),
                })
                l = 6
                qty_col = 6
                if not wb.cell_value(l-1, qty_col) == 'Quantity':
                    qty_col = 8
                for line in range(l,wb.nrows):
                    if wb.cell_value(line,1) not in [u'Your ProductNo','']:
                        product = self.env['product.product'].search([('default_code','=',wb.cell_value(line,1))])
                        if product:
                            _logger.warn('Rad %s  %s' % (wb.cell_value(line,1),wb.cell_value(line,qty_col)))
                            self.env['sale.order.line'].create({
                                        'order_id': order.id,
                                        'product_id': product.id,
                                        'product_uom_qty': int(wb.cell_value(line,qty_col)),
                                    })
                        else:
                            missing_products.append(wb.cell_value(line,1))
                            
                            
#
# Skin City XL
#
            if self[0].import_type == 'skincity_xl':
                customer = self.env['res.partner'].search([('name','=',self.get_selection_value('import_type',self.import_type))])
                order = create_order({
                    'partner_id': customer.id,
                    'client_order_ref': self.file_name.replace('.xlsx',''),
                })
                l = 1
                for line in range(l,wb.nrows):
                    if wb.cell_value(line,5) not in [u'Supplier art.nb','']:
                        product = self.env['product.product'].search([('default_code','=',wb.cell_value(line,5))])
                        if product:
                            _logger.warn('Rad %s  %s' % (wb.cell_value(line,5),wb.cell_value(line,7)))
                            self.env['sale.order.line'].create({
                                        'order_id': order.id,
                                        'product_id': product.id,
                                        'product_uom_qty': int(wb.cell_value(line,7)),
                                    })
                        else:
                            missing_products.append(wb.cell_value(line,5))

#
# Bangerhead AB
#
            if self[0].import_type == 'bangerhead':
                customer = self.env['res.partner'].search([('name','=',self.get_selection_value('import_type',self.import_type))])
                order = create_order({
                    'partner_id': customer.id,
                    'client_order_ref': self.file_name.replace('.xlsx',''),
                })
                l = 2
                for line in range(l,wb.nrows):
                    if wb.cell_value(line,2) not in [u'Art nr lev','']:
                        product = self.env['product.product'].search([('default_code','=',wb.cell_value(line,2))])
                        if product:
                            _logger.warn('Rad %s  %s' % (wb.cell_value(line,2),wb.cell_value(line,6)))
                            self.env['sale.order.line'].create({
                                        'order_id': order.id,
                                        'product_id': product.id,
                                        'product_uom_qty': int(wb.cell_value(line,6)),
                                    })
                        else:
                            missing_products.append(wb.cell_value(line,2))


        elif self[0].mime == 'text':
#
# Birka
#
            if self[0].import_type == 'birka':
                rp = re.compile('(\d{4}-\d{5}).* (\d+) \(ST\)')
                bnr = re.compile(u'beställ. nr: (\d+)')

                _logger.warn('bnr %s' % bnr.findall(self.order_file.decode('base64')))

                customer = self.env['res.partner'].search([('name', '=', self.get_selection_value('import_type', self.import_type))])
                order = create_order({
                    'partner_id': customer.id,
                    'client_order_ref': bnr.findall(self.order_file.decode('base64'))[0] if len(bnr.findall(self.order_file.decode('base64'))) > 0 else '',
                })

                for (prod,qty) in rp.findall(self.order_file.decode('base64')):
                    product = self.env['product.product'].search([('default_code','=',prod)])
                    if product:
                        self.env['sale.order.line'].create({
                                    'order_id': order.id,
                                    'product_id': product.id,
                                    'product_uom_qty': int(qty),
                                })
                    else:
                        missing_products.append(prod)
        elif self[0].mime == 'url':

            page = requests.get(self.order_url)
            tree = html.fromstring(page.content)
            specter_head = tree.xpath('//tr/td/font/text()')
            specter_lines = tree.xpath('//tr/td/nobr/text()')
            specter_qty = re.compile('(\d+) st')
#
# Tailwide
#
            if self.import_type == 'tailwide':
                customer = self.env['res.partner'].search([('name', '=', self.get_selection_value('import_type', self.import_type))])
                order = create_order({
                    'partner_id': customer.id,
                    'client_order_ref': specter_head[3] if len(specter_head) > 3 else '',
                })
                i = 0
                while i < len(specter_lines):
                    prod = specter_lines[i][:-1]
                    qty = specter_qty.findall(specter_lines[i+1])[0] if len(specter_qty.findall(specter_lines[i+1])) > 0 else 0
                    product = self.env['product.product'].search([('default_code', '=', prod)])
                    if product:
                        self.env['sale.order.line'].create({
                                    'order_id': order.id,
                                    'product_id': product.id,
                                    'product_uom_qty': int(qty),
                                })
                    else:
                        missing_products.append(prod)
                    i += 4

#
# Harmoniq AB
#
            if self.import_type == 'harmoniq':
                customer = self.env['res.partner'].search([
                    ('name', '=', self.get_selection_value('import_type', self.import_type))
                ])
                order = create_order({
                    'partner_id': customer.id,
                    'client_order_ref': specter_head[3] if len(specter_head) > 3 else '',
                })
                i = 0
                while i < len(specter_lines):
                    prod = specter_lines[i][:-1]
                    qty = specter_qty.findall(specter_lines[i+1])[0] if len(specter_qty.findall(specter_lines[i+1])) > 0 else 0
                    product = self.env['product.product'].search([('default_code', '=', prod)])
                    if product:
                        self.env['sale.order.line'].create({
                            'order_id': order.id,
                            'product_id': product.id,
                            'product_uom_qty': int(qty),
                        })
                    else:
                        missing_products.append(prod)
                    i += 4
#
# Åhléns AB
#
            if self.import_type == 'ahlens':
                ahlens_lines = tree.xpath('//table/tr')
                customer = self.env['res.partner'].search([('name', '=', self.get_selection_value('import_type', self.import_type))])
                # ~ raise Warning('%s ' %customer)
                plock = {}
                for line in ahlens_lines:
                    
                    if len(line) == 2:
                        if type(line[0].findtext('div')) == str and 'Plocklista' in line[0].findtext('div'):        
                            plock_idx = line[0].findtext('div')
                            order_ref_ids = line[1].findtext('div')
                            plock[plock_idx] = []
                                
                            # ~ raise Warning( '%s ' % order_ref_id)
                    if len(line) > 7:
                        product_ids = line[3].text
                        qtys = line[7].text
                        plock[plock_idx].append((product_ids, qtys))
                
                            # ~ prod = ahlens_lines[i][:-1]
                for pl in plock.keys():
                    order = create_order({
                        'partner_id': customer.id,
                        'client_order_ref': pl,
                        'origin' : order_ref_ids,
                    })
                    orders.append(order.id)
                    missing_products = []
                    for element in plock[pl]:
                        if not element[0] == 'Lev artnr':
                            
                            product = self.env['product.product'].search([('default_code', '=', element[0])])
                        
                            if product:
                                self.env['sale.order.line'].create({
                                            'order_id': order.id,
                                            'product_id': product.id,
                                            'product_uom_qty': int(element[1]),
                                        })
                            else:
                                missing_products.append(element[0])
                                # ~ i += 4
                    if len(missing_products) > 0:
                        order.note = 'Saknade produkter: ' + ','.join(missing_products)
                    order.note = '%s%s\n%s / %s' %('Saknade produkter:' if len(missing_products) > 0 else '', ','.join(missing_products) if len(missing_products) >0 else '', order_ref_ids,pl.replace('Plocklista ', ''))
                    if order:
                        attachment = self.env['ir.attachment'].create({
                        'name': order.client_order_ref or 'Order' + '.' + self.mime,
                        'res_name': order.name,
                        'res_model': 'sale.order',
                        'res_id': order.id,
                        'datas': self.order_file,
                        'store_fname': order.client_order_ref,
                    })
                

            
#
# END
#
        if not self.import_type == 'ahlens':
            if missing_products and order:
                order.note = 'Saknade produkter: ' + ','.join(missing_products)
            if order:
                attachment = self.env['ir.attachment'].create({
                        'name': order.client_order_ref or 'Order' + '.' + self.mime,
                        'res_name': order.name,
                        'res_model': 'sale.order',
                        'res_id': order.id,
                        'datas': self.order_file,
                        'store_fname': order.client_order_ref,
                    })
                #~ if attachment.mimetype == 'application/pdf':
                    #~ attachment.pdf2image(800,1200)
        
        if len(orders) > 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_ids': [(0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('sale.view_quotation_tree').id}),
                            (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('sale.view_order_form').id})],
                'res_id': order.id if order else None,
                'target': 'current',
                'context': {},
                'domain': [('id', 'in', orders)],
            }
        else:
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
