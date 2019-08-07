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
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import json

import logging
_logger = logging.getLogger(__name__)

class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    
    base = fields.Selection(
        selection_add=[('base_price', 'Base Price')],
        help='Base price for computation.\n'
             'Public Price: The base price will be the Sale/public Price.\n'
             'Cost Price : The base price will be the cost price.\n'
             'Base Price: The base price for currency conversion.\n'
             'Other Pricelist : Computation of the base price based on another Pricelist.')
    base_price_order = fields.Integer(string='Base Price Order', compute='_compute_base_price_order', store=True, help="Help field to check currency conversion rules before other rules.")
    from_currency_id = fields.Many2one(
        'res.currency',
        'Convert From Currency',
        help="Apply currency conversion from this currency to the pricelist currency.")
    currency_exchange_rate = fields.Float('Current Exchange Rate', compute='compute_exchange_rate', help="This is the current exchange rate. This will change with the exchange rates of the currencies involved.")
    
    @api.one
    @api.depends('categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price', \
        'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge', 'base')
    def _get_pricelist_item_name_price(self):
        super(PricelistItem, self)._get_pricelist_item_name_price()
        if self.compute_price == 'formula' and self.base == 'base_price':
            self.name += _(' (converted from Base Currency)')
        elif self.from_currency_id:
            self.name += _(' (converted from %s)') % self.from_currency_id.display_name
    
    @api.one
    @api.depends('base', 'compute_price')
    def _compute_base_price_order(self):
        if self.compute_price == 'formula' and self.base == 'base_price':
            self.base_price_order = 0
        else:
            self.base_price_order = 1
    
    @api.one
    @api.constrains('base', 'from_currency_id')
    def _check_from_currency_id(self):
        if self.base == 'base_price' and self.from_currency_id:
            raise ValidationError(_("Rule %s:\nYou can not use Base Price and Convert From Currency together.") % self.name)
    
    @api.one
    @api.depends('from_currency_id')
    def compute_exchange_rate(self):
        rate = 0.0
        if self.from_currency_id and self.currency_id:
            rate = self.env['res.currency']._get_conversion_rate(self.from_currency_id, self.currency_id)
        self.currency_exchange_rate = rate
    
    def apply_currency_exchange(self, price):
        return price * self.currency_exchange_rate

    @api.onchange('base', 'base_pricelist_id', 'compute_price', 'from_currency_id')
    def onchange_set_currency(self):
        if self.compute_price != 'formula':
            return
        if self.base == 'base_price':
            self.from_currency_id = None
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
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        If date in context: Date of the pricelist (%Y-%m-%d)

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.context_today(self)
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        self._cr.execute(
            'SELECT item.id '
            'FROM product_pricelist_item AS item '
            'LEFT JOIN product_category AS categ '
            'ON item.categ_id = categ.id '
            'WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))'
            'AND (item.product_id IS NULL OR item.product_id = any(%s))'
            'AND (item.categ_id IS NULL OR item.categ_id = any(%s)) '
            'AND (item.pricelist_id = %s) '
            'AND (item.date_start IS NULL OR item.date_start<=%s) '
            'AND (item.date_end IS NULL OR item.date_end>=%s)'
            ### CHANGED ###
            # Added base_price_order
            'ORDER BY item.applied_on, item.base_price_order, item.min_quantity desc, categ.parent_left desc',
            ######
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))

        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.env['product.pricelist.item'].browse(item_ids)
        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['product.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute('list_price')[product.id]

            price_uom = self.env['product.uom'].browse([qty_uom_id])
            for rule in items:
                # ~ _logger.warn('\n\nid: %s\nname: %s\n' % (rule.id, rule.name))
                ### ADDED ###
                # Check if Base Price can be applied to this product
                if rule.compute_price == 'formula' and rule.base == 'base_price' and not product.base_currency_id:
                    continue
                ######
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)])[product.id][0]  # TDE: 0 = price, 1 = rule
                    price = rule.base_pricelist_id.currency_id.compute(price_tmp, self.currency_id, round=False)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]

                convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'percentage':
                        price = (price - (price * (rule.percent_price / 100))) or 0.0
                    else:
                        # complete formula
                        price_limit = price
                        price = (price - (price * (rule.price_discount / 100))) or 0.0
                        if rule.price_round:
                            price = tools.float_round(price, precision_rounding=rule.price_round)

                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(rule.price_surcharge)
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(rule.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(rule.price_max_margin)
                            price = min(price, price_limit + price_max_margin)
                    suitable_rule = rule
                break
            # ~ if suitable_rule:
                # ~ _logger.warn('\n\nsuitable_rule id: %s\nname: %s\n' % (suitable_rule.id, suitable_rule.name))
            # Final price conversion into pricelist currency
            ### CHANGED ###
            if suitable_rule and suitable_rule.from_currency_id:
                price = suitable_rule.apply_currency_exchange(price)
            elif suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                if suitable_rule.base == 'base_price':
                    # Handle base price currency conversion
                    price = product.base_currency_id.compute(price, self.currency_id, round=False)
                else:
                    # Original currency conversion
                    price = product.currency_id.compute(price, self.currency_id, round=False)    
            ######

            results[product.id] = (price, suitable_rule and suitable_rule.id or False)

        return results
