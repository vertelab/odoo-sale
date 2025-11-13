import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_id_warning(self):
        warning = super(SaleOrder,self)._onchange_partner_id_warning()
     
        if warning:
            warning = warning.get("warning")
            _logger.error(f"{warning=}")
            return {
                'type': 'ir.actions.act_window',
                'name': f'{warning.get("title")}',
                'res_model': 'sale.order.warning.wizard',
                'view_mode': 'form',
                'target': 'new',  
                'context': {
                    'default_message': warning.get("message"),
                    "default_partner_id": self.partner_id.id
                    },
                }
