from odoo import models, fields, api, _


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    invoice_currency_id = fields.Many2one("res.currency", string="Invoice Currency")