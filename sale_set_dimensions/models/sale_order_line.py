from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty = fields.Integer()
    hight = fields.Float()
    width = fields.Float()
    from_uom = fields.Many2one(related="product_id.from_uom")
    should_set_dimensions = fields.Boolean(related="product_id.should_set_dimensions")

    @api.depends('display_type', 'product_id', 'product_packaging_qty', 'qty', 'hight', 'width', 'product_id.should_set_dimensions')
    def _compute_product_uom_qty(self):
        super(SaleOrderLine,self)._compute_product_uom_qty()
        for line in self:
            if line.product_id.should_set_dimensions:
                line.product_uom_qty = self.convert_uom(line.qty * line.hight * line.width)


    def convert_uom(self,qty):

        from_uom = self.from_uom
        to_uom = self.product_uom

        qty_in_ref = qty / (from_uom.factor * from_uom.factor)

        qty_uom_new = qty_in_ref * to_uom.factor
        
        round_amount = tools.float_round(qty_uom_new, precision_rounding=to_uom.rounding, rounding_method='UP')

        return round_amount


