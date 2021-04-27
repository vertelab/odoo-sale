# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    manufacturer = fields.Char(related='product_id.manufacturer')
    phone = fields.Char(related='order_partner_id.phone')
    contact_address = fields.Char(related='order_partner_id.contact_address')
    form_of_agreement = fields.Selection(related='agreement.form_of_agreement')
    license_start = fields.Datetime(string="License start")
    license_stop = fields.Datetime(
        string="License end",
        compute="_compute_license_stop",
        store=True,
    )
    agreement = fields.One2many(
        comodel_name='agreement',
        inverse_name='sale_order_line_ids',
    )
    code = fields.Char(
        related='order_id.agreement.code',
        # ~ string='Agreement Code',
        string='Avtalsnummer',
    )
    license_duration = fields.Integer(
        string="Duration",
        help="The duration in days",
    )

    # Function to calulate when a license has its end-date
    @api.depends('license_start')
    def _compute_license_stop(self):
        for record in self:
            if record.license_start:
                record.license_stop = record.license_start + timedelta(
                    days=record.license_duration)
            else:
                record.license_stop = False
