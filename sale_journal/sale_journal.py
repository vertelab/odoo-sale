# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution, third party
#    Copyright (C) 2019 Vertel AB.
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


from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class sale_journal_invoice_type(models.Model):
    _name = 'sale_journal.invoice.type'
    _description = 'Invoice Types'
    name = fields.Char(string='Invoice Type', required=True)
    active = fields.Boolean(string='Active', help="If the active field is set to False, it will allow you to hide the invoice type without removing it.",default=True)
    note = fields.Text(string='Note')
    invoicing_method = fields.Selection([('simple', 'Non grouped'), ('grouped', 'Grouped')], string='Invoicing method', required=True,default='simple')


#==============================================
# sale journal inherit
#==============================================

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    invoice_type_id = fields.Many2one(string="Invoicing Type", comodel_name='sale_journal.invoice.type',help = "This invoicing type will be used, by default, to invoice the current partner.")

    @api.one
    def x_commercial_fields(self):
        return super(res_partner, self)._commercial_fields() + ['invoice_type']

class picking(models.Model):
    _inherit = "stock.picking"
    invoice_type_id = fields.Many2one(comodel_name='sale_journal.invoice.type', string='Invoice Type', readonly=True)


class stock_move(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_confirm(self):
        """
            Pass the invoice type to the picking from the sales order
            (Should also work in case of Phantom BoMs when on explosion the original move is deleted, similar to carrier_id on delivery)
        """
        procs_to_check = []
        for move in self:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.invoice_type_id:
                procs_to_check += [move.procurement_id]
        res = super(stock_move, self).action_confirm()
        for proc in procs_to_check:
            for picking in list(set([x.picking_id for x in proc.move_ids if x.picking_id and not x.picking_id.invoice_type_id])):
                picking.invoice_type_id = proc.sale_line_id.order_id.invoice_type_id.id
        return res


class sale(models.Model):
    _inherit = "sale.order"
    invoice_type_id = fields.Many2one(comodel_name='sale_journal.invoice.type', string='Invoice Type',help="Generate invoice based on the selected option.")

    @api.one
    @api.onchange('partner_id') # depends
    def _set_invoice_type(self):
        self.invoice_type_id = self.partner_id.invoice_type_id.id if self.partner_id.invoice_type_id else None

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
