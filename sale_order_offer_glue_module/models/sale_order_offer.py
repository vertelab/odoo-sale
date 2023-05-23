# coding: utf-8

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class SaleOrderOffer(models.Model):
    _inherit = 'sale.order'

    sale_company_type = fields.Selection([
        ("person","Person"),
        ("company","Company")
    ], compute="_compute_company_type", readonly=False)

    def _compute_company_type(self):
        for offer in self:
            offer.sale_company_type = offer.partner_id.commercial_partner_id.company_type
                
            


