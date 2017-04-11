# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
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
from datetime import timedelta
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    customer_date = fields.Date(string='Customer Since', default=fields.Date.today)

class SaleCommission(models.Model):
    _inherit = "sale.commission"
    
    commission_type = fields.Selection(selection_add=[("rules", "Rules")])
    commission_rule_ids = fields.One2many(comodel_name='sale.commission.rule', inverse_name='commission_id', copy=True)
    
    @api.multi
    def calculate_rules(self, line):
        self.ensure_one()
        for rule in self.commission_rule_ids.sorted():
            if rule.match_rule(line):
                return line.price_subtotal * rule.percent / 100.0
        return 0
        

class SaleCommissionRule(models.Model):
    _name = "sale.commission.rule"
    _description = "Commission Rule"
    _order = 'sequence desc'
    
    name = fields.Char(string='Name', required=True)
    commission_id = fields.Many2one('sale.commission', string='Commission')
    sequence = fields.Integer(string='Sequence', default=100, required=True)
    product_ids = fields.Many2many(comodel_name='product.product', string='Product')
    product_tmpl_ids = fields.Many2many(comodel_name='product.template', string='Product Template')
    categ_ids = fields.Many2many(comodel_name='product.category', string='Product Category')
    min_age = fields.Integer(string="Partner Age", help="The minimum age (in days) of the partner to match this rule.")
    percent = fields.Float(string="Percent", required=True)
    
    @api.multi
    def match_rule(self, line):
        self.ensure_one()
        if self.product_ids and line.product_id not in self.product_id:
            return False
        if self.product_tmpl_ids and line.product_id.product_tmpl_id not in self.product_tmpl_id:
            return False
        if self.categ_ids and line.product_id.categ_id not in self.categ_ids:
            return False
        if self.min_age and not line.order_partner_id.customer_date or (fields.Date.from_string(line.order_id.date_order) - fields.Date.from_string(line.order_partner_id.customer_date)).days < self.min_age:
            return False
        return True

class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    @api.depends('commission.commission_type', 'sale_line.price_subtotal',
                 'commission.amount_base_type', 'sale_line.order_partner_id', 'sale_line.product_id')
    def _compute_amount(self):
        for line_agent in self:
            if (line_agent.commission.commission_type == 'rules' and not line_agent.sale_line.product_id.commission_free):
                line_agent.amount = line_agent.commission.calculate_rules(line_agent.sale_line)
            else:
                super(SaleOrderLineAgent, line_agent)._compute_amount()
