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
import json

import logging
_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = 'res.partner'

                
    def _get_sale_orders_data(self, cr, uid, ids, field_name, arg, context=None):
        obj = self.pool['sale.order']
        month_begin = date.today().replace(day=1)
        date_begin = (month_begin - relativedelta.relativedelta(months=self._period_number - 1)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        date_end = month_begin.replace(day=calendar.monthrange(month_begin.year, month_begin.month)[1]).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

        res = {}
        for id in ids:
            res[id] = {}
            created_domain = [('section_id', '=', id), ('state', 'in', ['draft', 'sent']), ('date_order', '>=', date_begin), ('date_order', '<=', date_end)]
            validated_domain = [('section_id', '=', id), ('state', 'not in', ['draft', 'sent', 'cancel']), ('date_order', '>=', date_begin), ('date_order', '<=', date_end)]
            res[id]['monthly_quoted'] = json.dumps(self.__get_bar_values(cr, uid, obj, created_domain, ['amount_total', 'date_order'], 'amount_total', 'date_order', context=context))
            res[id]['monthly_confirmed'] = json.dumps(self.__get_bar_values(cr, uid, obj, validated_domain, ['amount_untaxed', 'date_order'], 'amount_untaxed', 'date_order', context=context))
        return res

    @api.one
    def _kpi_sales_y1(self):
        today = fields.Datetime.now()
        #~ y1_start = fields.Datetime.to_string(year=-1,month=1,day=1)
        #~ y2_start = fields.Datetime.to_string(year=-2,month=1,day=1)
        #~ y3_start = fields.Datetime.to_string(year=-3,month=1,day=1)
        #~ self.kpi_sales_y1 = sum(self.sale_order_ids.filtered(lambda o: o.date >= y1_start ).mapped('amount_untaxed'))
        #~ self.kpi_sales_y2 = sum(self.sale_order_ids.filtered(lambda o: o.date >= y2_start and o.date < y1_start ).mapped('amount_untaxed'))
        #~ self.kpi_sales_y3 = sum(self.sale_order_ids.filteroed(lambda o: o.date >= y3_start and o.date < y2_start ).mapped('amount_untaxed'))
        self.kpi_sales_y3 =  '[{"values": [ {"value": 584.0, "label": "Anteriores"}, {"value": 739.73, "label": "29 feb-6 mar"}, {"value": 506.12, "label": "Esta semana"}, {"value": 233.6, "label": "14-20 mar"}, {"value": 0.0, "label": "21-27 mar"}, {"value": 0.0, "label": "Futuras"} ], "id": 2}]'
        self.monthly_quoted =  '[{"values": [ {"value": 584.0, "label": "Anteriores"}, {"value": 739.73, "label": "29 feb-6 mar"}, {"value": 506.12, "label": "Esta semana"}, {"value": 233.6, "label": "14-20 mar"}, {"value": 0.0, "label": "21-27 mar"}, {"value": 0.0, "label": "Futuras"} ], "id": 2}]'
        #self.monthly_quoted = json.dumps(self.env['sale.order'].__get_bar_values( [ ('state', 'in', ['draft', 'sent']), ], ['amount_total', 'date_order'], 'amount_total', 'date_order'))
    
    monthly_quoted = fields.Char(compute="_kpi_sales_y1")
    kpi_sales_y1 = fields.Char(compute="_kpi_sales_y1")
    kpi_sales_y2 = fields.Char(compute="_kpi_sales_y1")
    kpi_sales_y3 = fields.Char(compute="_kpi_sales_y1")
    # https://www.odoo.com/apps/modules/8.0/web_kanban_graph/
    