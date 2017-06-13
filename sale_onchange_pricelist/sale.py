# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2017- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, fields, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _inherit ='sale.order'

    @api.multi
    @api.onchange('pricelist_id', 'order_line')
    def onchange_pricelist_2_product(self):
        if self.pricelist_id:
            self.currency_id = self.pricelist_id.currency_id
            for line in self.order_line:
                vals = line.product_id_change(
                    self.pricelist_id.id,
                    line.product_id.id,
                    qty=line.product_uom_qty,
                    uom=line.product_uom.id,
                    qty_uos=line.product_uos_qty,
                    uos=False,
                    name=line.name,
                    partner_id=self.partner_id.id,
                    lang=False,
                    update_tax=True,
                    date_order=self.date_order,
                    packaging=False,
                    fiscal_position=self.fiscal_position.id,
                    flag=False
                ).get('value', {})
                for key in vals:
                    setattr(line, key, vals[key])
