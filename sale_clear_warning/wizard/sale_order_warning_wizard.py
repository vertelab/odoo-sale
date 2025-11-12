import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class SaleOrderWarningWizard(models.TransientModel):
    _name = 'sale.order.warning.wizard'
    _description = 'A wizard thet replaces the standard warning in odoo'

    message = fields.Char()
    partner_id = fields.Many2one(comodel_name="res.partner")

    def disable_warning(self):
        self.partner_id.write({"sale_warn": "no-message"})
