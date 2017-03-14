# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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
import logging
_logger = logging.getLogger(__name__)

class sale_journal_invoice_type(models.Model):
    _inherit = 'sale_journal.invoice.type'
    
    admin_fee = fields.Many2one(comodel_name="product.product",string="Administration Fee")
    
class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    @api.multi
    def action_invoice_create(self,journal_id, group=False, type='out_invoice'):
        #~ raise Warning(self,journal_id,group,type)
    # TODO: fiscal_position
        partner = {}
        for picking in self:
            if picking.sale_id.invoice_type_id and picking.sale_id.invoice_type_id.admin_fee:
                partner[picking.sale_id.partner_invoice_id.id if picking.sale_id.partner_invoice_id else picking.sale_id.partner_id.id] = {
                    'order_id': picking.sale_id.id,
                    'account_id': picking.sale_id.invoice_type_id.admin_fee.property_account_income.id if picking.sale_id.invoice_type_id.admin_fee.property_account_income else picking.sale_id.invoice_type_id.admin_fee.categ_id.property_account_income_categ.id,
                    'origin': picking.sale_id.name,
                    'fiscal_position': picking.sale_id.fiscal_position,
                    'product': picking.sale_id.invoice_type_id.admin_fee if picking.sale_id.invoice_type_id and picking.sale_id.invoice_type_id.admin_fee else None,
                    'project': picking.sale_id.project_id.id if picking.sale_id.project_id else None,
                }
        invoices = super(stock_picking, self).action_invoice_create(journal_id, group, type) 
        for invoice in self.env['account.invoice'].browse(invoices):
            #~ raise Warning(partner,partner[invoice.partner_id.id])
            if partner.get(invoice.partner_id.id):
                invoice.invoice_line = [(0,0,{
                    'account_id': partner[invoice.partner_id.id]['account_id'],
                    'name': partner[invoice.partner_id.id]['product'].name,
                    'sequence': 999,
                    'origin': partner[invoice.partner_id.id]['origin'],
                    'price_unit': partner[invoice.partner_id.id]['product'].lst_price,
                    'quantity': 1,
                    'product_id': partner[invoice.partner_id.id]['product'].id,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in partner[invoice.partner_id.id]['product'].taxes_id])],
                    'account_analytic_id': partner[invoice.partner_id.id]['project'],
                 })]
        return invoices
  
class sale_order(models.Model):
    _inherit = 'sale.order'
    # TODO: fiscal_position
    # TODO: Other invoice types than "Invoice the whole order"
    @api.multi
    def action_invoice_create(self, grouped=False, states=None, date_invoice = False):
        self.ensure_one()
        invoice_id = super(sale_order, self).action_invoice_create(grouped, states, date_invoice)
        for invoice in self.env['account.invoice'].browse(invoice_id):
            if self.invoice_type_id and self.invoice_type_id.admin_fee:
                account_id = self.invoice_type_id.admin_fee.property_account_income.id if self.invoice_type_id.admin_fee.property_account_income else self.invoice_type_id.admin_fee.categ_id.property_account_income_categ.id
                #~ raise Warning(order.invoice_type_id.admin_fee.categ_id.property_account_income_categ)
                invoice.invoice_line = [(0,0,{
                    'account_id': account_id,
                    'name': self.invoice_type_id.admin_fee.name,
                    'sequence': 999,
                    'origin': self.name,
                    'price_unit': self.invoice_type_id.admin_fee.lst_price,
                    'quantity': 1,
                    'product_id': self.invoice_type_id.admin_fee.id,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in self.invoice_type_id.admin_fee.taxes_id])],
                    'account_analytic_id': self.project_id.id if self.project_id else None,
                 })]
        return invoice_id
