from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class Product(models.Model):
    _inherit = 'product.product'

    @api.model
    def _domain_from_uom(self):
        length_categ = self.env.ref("uom.uom_categ_length")
        return [('category_id', '=', length_categ.id)]

    should_set_dimensions = fields.Boolean(default=False)
    from_uom = fields.Many2one(comodel_name="uom.uom", string="From dimensions", help="The unit of measure that the dimensions will be in.", domain=lambda self: self._domain_from_uom())

