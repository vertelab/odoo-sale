# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2018 Vertel AB (<http://vertel.se>).
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
import logging
_logger = logging.getLogger(__name__)


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    barcode_scanned = fields.Char(string='Scanned')

    @api.onchange('barcode_scanned')
    def onchange_barcode_scanned(self):
        if self.barcode_scanned:
            self.product_id = self.env['product.product'].search([('barcode', '=', self.barcode_scanned)])
