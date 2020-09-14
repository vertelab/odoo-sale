# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2017- Vertel AB (<http://vertel.se>).
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
from openerp.exceptions import Warning
from datetime import datetime, timedelta, date, time 

import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _inherit ='sale.order'
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        product.get_pricelist_chart_line(pricelist)
        return super(sale_order.self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
    
    @api.multi
    @api.onchange('pricelist_id')
    def onchange_pricelist_2_product(self):
        if self.pricelist_id:
            self.currency_id = self.pricelist_id.currency_id
            order_line = []
            for line in self.order_line:
                line.product_id.get_pricelist_chart_line(self.pricelist_id)
                vals = line.product_id_change(
                    self.pricelist_id.id,
                    line.product_id.id,
                    qty=line.product_uom_qty,
                    uom=line.product_uom.id,
                    qty_uos=line.product_uos_qty,
                    uos=False,
                    name=line.name,
                    partner_id=self.partner_id.id,
                    lang=False,
                    update_tax=True,
                    date_order=self.date_order,
                    packaging=False,
                    fiscal_position=self.fiscal_position.id,
                    flag=False
                ).get('value', {})
                order_line.append((1, line.id, vals))
            self.write({'order_line': order_line})
    
     
    # ~ def cron_update_sale_date(self):
        # ~ today = fields.Date.today() 
        # ~ time_limit = datetime.now() + timedelta(minutes=float(self.env['ir.config_parameter'].get_param('sale_onchange_pricelist.time_limit', '4')))
        # ~ order_names = []
        # ~ for pricelist in self.env['product.pricelist'].search([]):
            # ~ if datetime.now() > time_limit:
                # ~ break
            # ~ # Hitta datum för senaste ändring
            # ~ current_version = self.env['product.pricelist.version'].search([
                # ~ ('pricelist_id', '=', pricelist.id),
                # ~ ('active', '=', True),
                # ~ ('date_start', '=', today)]
    
                # ~ limit=1, order='date_start')
            # ~ if not current_version:
                # ~ continue
            # ~ # Sök fram en order som har ett tidigare datum
            # ~ domain = [
                # ~ ('date_order', '<', current_version.date_start),
                # ~ ('state', '=', 'draft'),
                # ~ ('pricelist_id', '=', pricelist.id)]
            # ~ order = self.env['sale.order'].search(domain, limit=1)
            # ~ while (datetime.now() < time_limit) and order:
                # ~ # Uppdatera datum osv
                # ~ order.date_order = fields.Datetime.now()
                # ~ order.onchange_pricelist_2_product()
                # ~ self.env.cr.commit()
                # ~ order_names.append(order.name)
                # ~ order = self.env['sale.order'].search(domain, limit=1)
        # ~ _logger.warn("Finished sale date update for %s orders: %s" % (len(order_names), ', '.join(order_names)))
    @api.model    
    def cron_update_sale_date(self):
        today = fields.Date.today() 
        order_names = []
        # ~ for pricelist in self.env['product.pricelist'].search([]):
            # Hitta datum för senaste ändring
        for current_version in self.env['product.pricelist.version'].search([
                ('active', '=', True),
                ('date_start', '=', today)]):
            
            pricelist_type_ids = self.env['pricelist_chart.type'].search([
                 '|', ('pricelist', '=', current_version.pricelist_id.id),
                      ('rec_pricelist', '=', current_version.pricelist_id.id)
            ]).mapped('id')

            for pl in self.env['product.pricelist_chart'].search([('pricelist_chart_id', 'in', pricelist_type_ids)]):
               pl.unlink()

        # Sök fram en order som har ett tidigare datum
            domain = [
                # ~ ('date_order', '<=', current_version.date_start),
                # ('customer_no', '=', '9071'), # Testing on La casa mia orders, for Skogsro use '1213'
                ('state', '=', 'draft'),
                ('pricelist_id', '=', current_version.pricelist_id.id)]
           
            for order in self.env['sale.order'].search(domain):
                # Uppdatera datum osv
                order.date_order = fields.Datetime.now()
                order.onchange_pricelist_2_product()
                self.env.cr.commit()
                order_names.append(order.name)
            
                # ~ get_product_detail()
                
                # ~ key_raw = 'product_detail %s %s %s %s %s %s %s' % (
                    # ~ self.env.cr.dbname, 
                    # ~ product.id, 
                    # ~ variant_id,
                    # ~ pricelist.id, 
                    # ~ self.env.lang, 
                    # ~ memcached_time,
                    # ~ self.env.user in self.sudo().env.ref('base.group_website_publisher').users)
                    
                    # ~ get_thumbnail_default_variant()
                    
                    # ~ key_raw = 'thumbnail_default_variant %s %s %s %s' % (
                        # ~ self.env.cr.dbname, 
                        # ~ product['id'], 
                        # ~ pricelist.id, 
                        # ~ self.env.lang)   # db produkt prislista språk
                        
                    # ~ get_thumbnail_variant()
                    # ~ key_raw = 'thumbnail_variant %s %s %s %s' % (
                        # ~ self.env.cr.dbname, 
                        # ~ variant['id'], 
                        # ~ pricelist.id, 
                        # ~ self.env.lang)
                        
                    # ~ get_list_row()
                    # ~ key_raw = 'list_row %s %s %s %s %s %s %s Groups: %s' % (self.env.cr.dbname, flush_type, product['id'], pricelist.id, self.env.lang, request.session.get('device_type', 'md'), product['memcached_time'], request.website.get_dn_groups())  # db flush_type produkt prislista språk användargrupp
                    
                    #TODO: add pricelist to website.put_page_dict(index_key = "pricelist %s" %pricelist) and build index_key of the pricelist 
                    #TODO: website.remove_page_index(index_key)
                
                    
        _logger.warn("Finished sale date update for %s orders: %s" % (len(order_names), ', '.join(order_names)))
        
        
    @api.model
    def remove_page_dict(self, key_raw):
        key = self.env['website'].remove_page_dict()
        MEMCACHED.mc_save(key, page_dict,24 * 60 * 60 * 7)  # One week
        memcached.mc_delete(key)  # One week
        
    @api.model    
    def cron_update_currency_rate(self):
        today = fields.Date.today() 
        order_names = []

        for current_rate in self.env['res.currency.rate'].search([
            ('name', '>', fields.Date.to_string( (fields.Datetime.from_string(today) + timedelta(days=-1)) )),
            ('name', '<', fields.Date.to_string( (fields.Datetime.from_string(today) + timedelta(days=1)) ))
            ]):

            for pricelist in self.env['product.pricelist'].search([('currency_id','=', current_rate.currency_id.id)]):

                domain = [
                    ('state', '=', 'draft'),
                    ('pricelist_id', '=', pricelist.id)
                ]

                order_names = []
                for order in self.env['sale.order'].search(domain):
                    # Uppdatera datum osv
                    order.date_order = fields.Datetime.now()
                    order.onchange_pricelist_2_product()
                    self.env.cr.commit()
                    order_names.append(order.name)

        _logger.warn("Finished currency rate update for %s orders: %s" % (len(order_names), ', '.join(order_names)))