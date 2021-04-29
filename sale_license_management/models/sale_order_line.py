# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError
from datetime import timedelta, date

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    now = date.today()
    manufacturer = fields.Char(related='product_id.manufacturer')
    phone = fields.Char(related='order_partner_id.phone')
    contact_address = fields.Char(related='order_partner_id.contact_address')
    form_of_agreement = fields.Selection(related='agreement.form_of_agreement')
    agreement = fields.One2many(
        comodel_name='agreement',
        inverse_name='sale_order_line_ids',
    )
    code = fields.Char(
        related='order_id.agreement.code',
        string='Avtalsnummer',
    )
    license_start = fields.Date(
        string="License start",
        related="order_id.agreement.start_date",
    )
    agreement_end_date = fields.Date(related="order_id.agreement.end_date")
    license_stop = fields.Date(
        string="License end",
        required=True,
        compute='_end_date',
    )
    stand_alone_end_date_check = fields.Boolean(
        string='Annat slutdatum',
        default=False,
    )
    stand_alone_end_date = fields.Date(
        string='Slutdatum',
        default=now+timedelta(days=365),
    )

    @api.onchange('stand_alone_end_date_check', 'stand_alone_end_date')
    def _end_date(self):
        for record in self:
            if record.stand_alone_end_date_check:
                record.license_stop = record.stand_alone_end_date
            else:
                record.license_stop = record.agreement_end_date
            if record.stand_alone_end_date and (record.stand_alone_end_date < record.license_stop):
                record.license_stop = record.license_start
                record.stand_alone_end_date = record.license_start
            else:
                pass
