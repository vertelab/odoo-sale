from odoo import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)

class Product(models.Model):
    _inherit = 'product.template'

    estimated_time = fields.Float(string='Estimated Time')