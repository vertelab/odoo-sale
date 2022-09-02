from odoo import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

class AnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    sale_invoice_type = fields.Selection([('default', 'Default'), ('static_price', 'Static Price'), ('product_price', 'Product_price')])

    

