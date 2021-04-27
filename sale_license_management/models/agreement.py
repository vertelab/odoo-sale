# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import datetime

class Agreement(models.Model):
    _inherit = 'agreement'

    # Connecting a sale order to agreement
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        # ~ string="Sale Order",
        string="Säljorder",
    )
    # Connecting sale order lines to agreement via sale order
    sale_order_line_ids = fields.One2many(
        comodel_name='sale.order.line',
        string="Sale Order Line",
        related="sale_order_id.order_line",
    )
    is_license = fields.Boolean(
        # ~ string='License Agreement',
        string='Licensavtal',
        default=False,
    )
    form_of_agreement = fields.Selection(
        selection=[('ea','EA'),('vip','VIP'), ('select','SELECT')],
        default="ea",
        # ~ string="Form of agreement",
        string='Avtalsform',
        help="Form of agreement",
    )
    notification_days = fields.Integer(
        # ~ string='Notification Days',
        string='Notifikationsdagar',
        help='The amount of days that a notification i sent out before the agreement end date',
        required=True,
    )
    notification_date = fields.Date(
        # ~ string='Notification Date',
        string='Notifikationsdatum',
        help=('The date when a notification is sent about the agreement \n\n'
            'If the implemented days are out of the scope, the notification date will be on the end date'),
        compute='_compute_notification'
    )

    """ ÖVERSÄTTNINGAR """
    code = fields.Char(string='Avtalsnummer')
    signature_date = fields.Date(string='Signatursdatum')
    start_date = fields.Date(string='Startdatum')
    end_date = fields.Date(string='Slutdatum')
    name = fields.Char(string='Namn')

    # Partner information
    partner_id = fields.Many2one(string='Kund') # Endast skapad för att ändra sträng
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

    # Function to send the notification on correct date
    def _send_notification(self):
        now = datetime.now()
        for record in self:
            if record.notification_date == datetime.date.today():
                raise Warning('Today we send a notification')
            else:
                raise Warning('Today we will not send a notification')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agreement = fields.One2many(
        comodel_name='agreement',
        inverse_name='sale_order_id',
        string='Agreement check',
        help='Looking for agreement check',
    )
