from odoo import models, api, _
from odoo.exceptions import UserError
#import logging
#_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange("product_id")
    def _partnercheck(self):
        if not self.order_partner_id:
            error = _('You need to set a Customer before you can add a product.')
            raise UserError(error)
