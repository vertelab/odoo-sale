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
import logging
_logger = logging.getLogger(__name__)

class sale_order_warning_wizard(models.TransientModel):
    _name = 'sale.order.warning.wizard'

    @api.multi
    def confirm(self):
        order = self.env['sale.order'].browse(self._context.get('active_id'))
        if order:
            order.action_button_confirm()

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
            return super(sale_order, self).action_button_confirm()
