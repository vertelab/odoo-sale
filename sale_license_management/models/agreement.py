# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError
from datetime import timedelta, date

# Form of Agreements
FOA = [
    ('select_plus', 'Select plus'),
    ('eas', 'EAS'),
    ('ea', 'EA'),
    ('ees', 'EES'),
    ('sce', 'SCE'),
    ('vip_c', 'VIP-C'),
    ('vip_g', 'VIP-G'),
    ('vip_e', 'VIP-E'),
    ('etla', 'ETLA'),
]

class Agreement(models.Model):
    _inherit = 'agreement'

    now = date.today()
    # Connecting a sale order to agreement
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string="Säljorder",
    )
    # Connecting sale order lines to agreement via sale order
    sale_order_line_ids = fields.One2many(
        comodel_name='sale.order.line',
        string="Sale Order Line",
        related="sale_order_id.order_line",
    )
    is_license = fields.Boolean(
        string='Licensavtal',
        default=False,
    )
    form_of_agreement = fields.Selection(
        FOA,
        default="select_plus",
        string='Avtalsform',
        help="Form of agreement",
    )
    notification_days = fields.Integer(
        string='Notifikationsdagar',
        help='The amount of days that a notification i sent out before the agreement end date',
        required=True,
    )
    notification_date = fields.Date(
        string='Notifikationsdatum',
        help=('The date when a notification is sent about the agreement \n\n'
            'If the implemented days are out of the scope, the notification date will be on the end date'),
        compute='_compute_notification',
    )

    code = fields.Char(string='Avtalsnummer')
    name = fields.Char(string='Namn')
    signature_date = fields.Date(
        string='Signatursdatum',
        default=now,
    )
    start_date = fields.Date(
        string='Startdatum',
        default=now,
    )
    end_date = fields.Date(
        string='Slutdatum',
        default=now+timedelta(days=365),
    )

    # Partner information
    partner_id = fields.Many2one(
        string='Kund',
    )
    phone = fields.Char(
        related='partner_id.phone',
        string="Kund - Telefon",
    )
    contact_address = fields.Char(
        related='partner_id.contact_address',
        string="Kund - Adress",
    )
    email = fields.Char(
        related='partner_id.email',
        string="Kund - Email",
    )

    # Function to calculate the date for when a notification should be sent
    @api.depends('end_date')
    def _compute_notification(self):
        for record in self:
            if record.end_date:
                record.notification_date = record.end_date - timedelta(
                    record.notification_days)
            else:
                record.notification_date = False
            if (record.notification_date < record.start_date
                or record.notification_date > record.end_date):
                record.notification_date = record.end_date
            else:
                pass
            if record.end_date < record.start_date:
                record.end_date = record.start_date
                raise ValidationError(_('The end date cannot be before the start date'))
            else:
                pass

    @api.onchange('partner_id')
    def _partner_id_check(self):
        for record in self:
            if record.partner_id != record.sale_order_id.partner_id:
                raise ValidationError(_(
                    'Agreement partner and Sale order partner are not the same'
                    '\nYour current sale order partner is %s'
                    %record.sale_order_id.partner_id.name
                ))
            else:
                pass

    @api.onchange('sale_order_id')
    def _partner_id_sale_partner(self):
        for record in self:
            record.partner_id = record.sale_order_id.partner_id
            record.sale_order_line_ids.license_start = record.start_date
            record.sale_order_line_ids.license_stop = record.end_date
            record.sale_order_line_ids.stand_alone_end_date = record.end_date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agreement = fields.One2many(
        comodel_name='agreement',
        inverse_name='sale_order_id',
        string='Agreement check',
        help='Looking for agreement check',
    )
