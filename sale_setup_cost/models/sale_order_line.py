from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    setup_cost_product_id = fields.Many2one(related="product_id.setup_cost_product_id")
    handling_cost_product_id = fields.Many2one(related="product_id.handling_cost_product_id")
    setup_cost = fields.Float(related="setup_cost_product_id.lst_price")
    handling_cost = fields.Float(related="handling_cost_product_id.lst_price")
   
