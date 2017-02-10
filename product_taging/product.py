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
from openerp.exceptions import except_orm, Warning, RedirectWarning

import logging
_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(selection_add=[('partner_tag', 'Partner Tag')])
    partner_categ_id = fields.Many2one(comodel_name='res.partner.category', string='Partner Tag')


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def need_procurement(self):
        res = False
        for line in self:
            if line.product_id and line.product_id.type == 'partner_tag' and line.product_id.partner_categ_id:
                line.order_id.partner_id.category_id = [(4, line.product_id.partner_categ_id.id, 0)]
            else:
                if super(sale_order_line, line).need_procurement():
                    res = True
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
