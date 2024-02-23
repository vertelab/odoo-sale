import logging
from odoo import fields, models, api, _
from odoo.tools.misc import formatLang, get_lang


_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.depends('product_id.type')
    def _compute_is_service(self):
        for so_line in self:
            so_line.is_service = so_line.product_id.type in ['service','consu','product']

    @api.depends('product_id.type')
    def _compute_product_updatable(self):
        for line in self:
            if line.product_id.type in ['service','consu','product'] and line.state == 'sale':
                line.product_updatable = False
            else:
                super(SaleOrderLine, line)._compute_product_updatable()
