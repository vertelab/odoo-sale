# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    license_start = fields.Datetime(string="License start")
    license_stop = fields.Datetime(string="License end", compute="_compute_license_stop", store=True)
    phone = fields.Char(related='order_partner_id.phone')
    contact_address = fields.Char(related='order_partner_id.contact_address')
    form_of_agreement = fields.Char(related='product_template_id.form_of_agreement')

    @api.depends('license_start')
    def _compute_license_stop(self):
        for record in self:
            if record.license_start and record.product_id:
                record.license_stop = record.license_start + timedelta(
                    days=record.product_id.license_duration)
            else:
                record.license_stop = False
