from odoo import fields, models, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    ready_to_deliver = fields.Boolean(string="Set Products to Ready to Deliver", default=False, readonly=True)
