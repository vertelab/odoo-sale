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
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    order_line_count = fields.Integer(string='Order Lines', compute='_get_order_line_count')
    
    @api.one
    def _get_order_line_count(self):
        self.order_line_count = self.env['sale.order.line'].search_count([('order_partner_id', '=', self.id)])
    
    @api.multi
    def action_view_order_lines(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window'].for_xml_id('customer_order_lines', 'action_order_line_tree')
        return action

class OrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    date_order = fields.Datetime(related='order_id.date_order', store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
