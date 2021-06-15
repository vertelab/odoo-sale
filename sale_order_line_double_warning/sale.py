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
import traceback

import logging
_logger = logging.getLogger(__name__)

class sale_order_warning_wizard(models.TransientModel):
    _name = 'sale.order.warning.wizard'
    _description = "Sale Order Warning Wizard"
    
    @api.model
    def default_order_id(self):
        return self.env['sale.order'].browse(self._context.get('active_id'))
        
    @api.one
    @api.depends('order_id')
    def compute_line_ids(self):
    # ~ def default_line_ids(self):
        # ~ order_id = self.env['sale.order'].browse(self._context.get('active_id'))
        order_id = self.order_id
        line_ids = self.env['sale.order.line'].browse()
        for product in order_id.order_line.mapped('product_id'):
            lines = order_id.order_line.filtered(lambda l: l.product_id == product)
            if len(lines) > 1:
                line_ids += lines
        self.line_ids = line_ids
    
    order_id = fields.Many2one(comodel_name='sale.order', string='Order', default=default_order_id, readonly=True)
    # ~ line_ids = fields.Many2many(comodel_name='sale.order.line', string='Order Lines', default=default_line_ids, readonly=True)
    line_ids = fields.Many2many(comodel_name='sale.order.line', string='Order Lines', compute='compute_line_ids')
    
    @api.multi
    def confirm(self):
        order = self.env['sale.order'].browse(self._context.get('active_id'))
        if order:
            return order.action_button_confirm()

class sale_order(models.Model):
    _inherit ='sale.order'

    @api.multi
    def action_button_confirm_check(self):
        if len(self.order_line.mapped('product_id')) < len(self.order_line):
            #~ raise myRedirectWarning(_("There're sale order lines contain same product"), self.env.ref('sale_order_line_double_warning.action_orders_check').id, _('Continue anyway'))
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order.warning.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('sale_order_line_double_warning.view_sale_order_warning_wizard_form').id,
                'target': 'new',
                'context': {'active_id': self.id},
            }
        else:
            return self.action_button_confirm()

class SaleOrderLine(models.Model):
    _inherit ='sale.order.line'
    
    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        if res.product_id and (len(res.order_id.order_line.filtered(lambda l: l.product_id == res.product_id)) > 1):
            tag = 'sale.order.line double trouble!! %s' % res.id
            tb = traceback.format_stack()
            msg = ('\n%s' % tag) + ''.join([line.replace('\n', '\n%s' % tag) for line in tb])
            _logger.warn(msg)
        return res
