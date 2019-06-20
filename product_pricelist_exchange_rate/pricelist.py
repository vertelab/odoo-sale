# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2019 Vertel AB (<http://vertel.se>).
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
from datetime import datetime, timedelta
import json

import logging
_logger = logging.getLogger(__name__)

class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    
    from_currency_id = fields.Many2one(
        'res.currency',
        'Convert From Currency',
        help="Apply currency conversion from this currency to the pricelist currency.")
    currency_exchange_rate = fields.Float('Current Exchange Rate', compute='compute_exchange_rate', help="This is the current exchange rate. This will change with the exchange rates of the currencies involved.")
    
    @api.one
    def compute_exchange_rate(self):
        rate = 0.0
        if self.from_currency_id and self.currency_id:
            rate = self.env['res.currency']._get_conversion_rate(self.from_currency_id, self.currency_id)
        self.currency_exchange_rate = rate
    
    def apply_currency_exchange(self, price):
        return price * self.currency_exchange_rate

    @api.onchange('base', 'base_pricelist_id', 'compute_price')
    def onchange_set_currency(self):
        if self.compute_price != 'formula':
            return
        if self.base != 'pricelist':
            return
        if not self.base_pricelist_id:
            return
        self.from_currency_id = self.base_pricelist_id.currency_id

class Pricelist(models.Model):
    _inherit = 'product.pricelist'
    
    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        result = super(Pricelist, self)._compute_price_rule(products_qty_partner, date=date, uom_id=uom_id)
        _logger.warn(result)
        for id, value in result.iteritems():
            if type(value) == tuple:
                price, rule_id = value
                if not rule_id:
                    continue
                rule = self.env['product.pricelist.item'].browse(rule_id)
                if rule.from_currency_id:
                    result[id] = (rule.apply_currency_exchange(price), rule_id) 
        return result
