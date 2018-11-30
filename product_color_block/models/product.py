# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018 Vertel (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class product_product(models.Model):
    _inherit = 'product.product'

    attribute_color_hex = fields.Char(string='Color', compute='_attribute_color_hex')
    @api.one
    def _attribute_color_hex(self):
        color_attributes = self.attribute_value_ids.filtered(lambda v: v.attribute_id.type == 'color')
        if len(color_attributes) > 0:
            self.attribute_color_hex = color_attributes[0].html_color
        else:
            self.attribute_color_hex = ''

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
