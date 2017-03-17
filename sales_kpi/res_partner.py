# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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
from openerp import models, fields, api, _
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def _kpi_sales_y1(self):
        today = fields.Datetime.today()
        y1_start = fields.Datetime.to_string(year=-1,month=1,day=1)
        y2_start = fields.Datetime.to_string(year=-2,month=1,day=1)
        y3_start = fields.Datetime.to_string(year=-3,month=1,day=1)
        self.kpi_sales_y1 = sum(self.sale_order_ids.filtered(lamda o: o.date >= y1_start ).mapped('amount_untaxed'))
        self.kpi_sales_y2 = sum(self.sale_order_ids.filtered(lamda o: o.date >= y2_start and o.date < y1_start ).mapped('amount_untaxed'))
        self.kpi_sales_y3 = sum(self.sale_order_ids.filtered(lamda o: o.date >= y3_start and o.date < y2_start ).mapped('amount_untaxed'))
    kpi_sales_y1 = fields.Integer(compute="_kpi_sales_y1")
    kpi_sales_y2 = fields.Integer(compute="_kpi_sales_y1")
    kpi_sales_y3 = fields.Integer(compute="_kpi_sales_y1")
    # https://www.odoo.com/apps/modules/8.0/web_kanban_graph/
    