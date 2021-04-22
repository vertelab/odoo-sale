# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Adding a alternative to object 'type' in product.template
    type = fields.Selection(
        selection_add=[('license','License')],
        ondelete={'license':'cascade'},
    )
    # Adding a manufacturer, the company that created the product.
    # This manufacturer may be implemented as a res.partner(?) in the future
    manufacturer = fields.Char(
        string='Manufacturer',
        help='The company that created the product',
    )
