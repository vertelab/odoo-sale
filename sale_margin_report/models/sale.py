# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018 Vertel (<http://vertel.se>).
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
import logging
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_ratio = fields.Float(compute='_product_margin_ratio', digits=dp.get_precision('Product Price'), store=True)

    @api.depends('product_id', 'purchase_price', 'product_uom_qty', 'price_unit', 'price_subtotal', 'margin')
    def _product_margin_ratio(self):
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            price = line.purchase_price
            if not price:
                from_cur = line.env.user.company_id.currency_id.with_context(date=line.order_id.date_order)
                price = from_cur.compute(line.product_id.standard_price, currency, round=False)
            if line.price_subtotal == 0.0:
                line.margin_ratio = 0.0
            else:
                line.margin_ratio = round(line.margin / line.price_subtotal, 4) * 100


# ~ class SaleReport(models.Model):
    # ~ _inherit = 'sale.report'

    # ~ margin_ratio = fields.Float(string='Margin Ratio', readonly=True)

    # ~ def _select(self):
        # ~ return super(SaleReport, self)._select() + ", (SUM(t.standard_price * l.product_uom_qty / u.factor * u2.factor) / SUM(l.price_subtotal / COALESCE(cr.rate, 1.0))) AS margin_ratio"

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
