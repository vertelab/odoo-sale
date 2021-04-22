# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError

class Agreement(models.Model):
    _inherit = 'agreement'

    # Connecting a sale order to agreement
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string="Sale Order",
    )
    # Connecting sale order lines to agreement via sale order
    sale_order_line_ids = fields.One2many(
        comodel_name='sale.order.line',
        string="Sale Order Line",
        related="sale_order_id.order_line",
    )
    is_license = fields.Boolean(
        string='License Agreement',
        default=False,
    )
    form_of_agreement = fields.Selection(
        selection=[('ea','EA'),('vip','VIP'), ('select','SELECT')],
        default="ea",
        string="Form of agreement",
        help="Form of agreement",
    )
    license_start = fields.Datetime(related="sale_order_line_ids.license_start")
    license_stop = fields.Datetime(related="sale_order_line_ids.license_stop")
    # Partner information
    phone = fields.Char(related='sale_order_id.partner_id.phone', string="Kund - Telefon")
    contact_address = fields.Char(related='sale_order_id.partner_id.contact_address', string="Kund - Adress")
    email = fields.Char(related='sale_order_id.partner_id.email', string="Kund - Email")



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agreement = fields.One2many(
        comodel_name='agreement',
        inverse_name='sale_order_id',
        string='Agreement check',
        help='Looking for agreement check',
    )
