from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_phone = fields.Char(string="Phone", related='partner_id.phone', readonly=False)

