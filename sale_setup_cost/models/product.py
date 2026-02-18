from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class Product(models.Model):
    _inherit = 'product.product'

    setup_type = fields.Selection([('normal','Normal'),('setup_cost','Setup Cost'),('handling_cost','Handling Cost')], default="normal")
    setup_cost_product_id = fields.Many2one(comodel_name="product.product")
    handling_cost_product_id = fields.Many2one(comodel_name="product.product")

