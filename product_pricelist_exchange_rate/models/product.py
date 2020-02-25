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
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    base_currency_id = fields.Many2one(comodel_name='res.currency', compute='compute_base_price', string='Base Currency')
    base_price = fields.Float(string='Base Price', compute='compute_base_price', digits=dp.get_precision('Product Price'), help="Base price in the base currency. Used to calculate prices in other currencies.")
    base_price_ids = fields.One2many(string='Base Prices', comodel_name='product.base.price', inverse_name='product_id')
    
    @api.one
    @api.depends('base_price_ids.price', 'base_price_ids.currency_id')
    def compute_base_price(self):
        # TODO: prices for a specific date. date in context?
        # _logger.warn('\n\ncompute_base_price\n%s\n' % self.env.context)
        date = (self.env.context.get('date', '') or fields.Date.today()).split(' ')[0]
        domain = [('product_id', '=', self.id), ('date_start', '<=', date), '|', ('date_end', '>', date), ('date_end', '=', False)]
        # _logger.warn(domain)
        base_price = self.env['product.base.price'].search(domain, limit=1, order='date_start asc')
        if base_price:
            self.base_currency_id = base_price.currency_id
            self.base_price = base_price.price
    
    @api.model
    def search_base_price(self, op, value):
        date = self.env.context.get('date') or fields.Date.today()
        # TODO: This wont work. We only want one hit per product_id. Need to write some SQL.
        bp_ids = [d['id'] for d in self.env['product.base.price'].search_read([('price', op, value), ('date_start', '<=', date), '|', ('date_end', '=', False), ('date_end', '>', date)], ['id'])]
        return [('base_price_ids', 'in', bp_ids)]

class ProductBasePrice(models.Model):
    _name = 'product.base.price'
    
    def default_date_start(self):
        return fields.Date.today()
    
    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True, ondelete='cascade')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Base Currency', required=True)
    price = fields.Float(string='Base Price', digits=dp.get_precision('Product Price'), help="Base price in the base currency. Used to calculate prices in other currencies.")
    date_start = fields.Date(string='Start Date', default=default_date_start, required=True)
    date_end = fields.Date(string='End Date', compute='compute_date_end', store=True, inverse='set_date_end')
    date_end_fixed = fields.Date(string='End Date (Fixed)')
    
    @api.one
    @api.depends('product_id.base_price_ids.price', 'product_id.base_price_ids.date_start', 'date_end_fixed')
    def compute_date_end(self):
        # _logger.warn('\n\ncompute_date_end\n%s %s\n' % (self.date_end, self.date_end_fixed))
        next_bp = self.search([('product_id', '=', self.product_id.id), ('date_start', '>', self.date_start)], limit=1, order='date_start')
        if next_bp:
            date_end = next_bp.date_start
        else:
            date_end = False
        if not date_end or (self.date_end_fixed and (self.date_end_fixed < date_end)):
            date_end = self.date_end_fixed
        self.date_end = date_end
    
    @api.one
    def set_date_end(self):
        self.date_end_fixed = self.date_end
    
    @api.one
    @api.constrains('product_id', 'date_start', 'date_end_fixed')
    def constrains_date_start(self):
        # TODO: Check for overlapping periods? (date_start - date_end_fixed)
        for bp in self.product_id.base_price_ids:
            if bp == self:
                continue
            if bp.date_start == self.date_start:
                raise ValidationError(_("A product can't have two base prices with the same start date (%s)") % self.date_start)

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """ Verifies that the operation given by ``operation`` is allowed for
            the current user according to the access rights.
        """
        # _logger.warn('\n\ncheck_access_rights: %s\n' % operation)
        if operation in ('create', 'unlink'):
            operation = 'write'
        return self.env['ir.model.access'].check('product.product', operation, raise_exception)
    
    @api.multi
    def check_access_rule(self, operation):
        """ Verifies that the operation given by ``operation`` is allowed for
            the current user according to ir.rules.

           :param operation: one of ``write``, ``unlink``
           :raise UserError: * if current ir.rules do not permit this operation.
           :return: None if the operation is allowed
        """
        # _logger.warn('\n\n%s.check_access_rule: %s\n' % (self, operation))
        if operation in ('create', 'unlink'):
            operation = 'write'
        return self.mapped('product_id').check_access_rule(operation)
