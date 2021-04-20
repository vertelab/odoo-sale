# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError

class Agreement(models.Model):
    _inherit = 'agreement'

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string="Sale Order",
    )
    sale_order_line_ids = fields.One2many(
        comodel_name='sale.order.line',
        string="Sale Order Line",
        related="sale_order_id.order_line",
    )
    is_license = fields.Boolean(
        string='License Agreement',
        default=False,
    )
    license_start = fields.Datetime(related="sale_order_line_ids.license_start")
    license_stop = fields.Datetime(related="sale_order_line_ids.license_stop")
    name = fields.Text(related="sale_order_line_ids.name")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agreement = fields.One2many(
        comodel_name='agreement',
        inverse_name='sale_order_id',
        string='Agreement check',
        help='Looking for agreement check',
    )
    
