from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('type', '=', 'invoice')]", )