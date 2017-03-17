# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
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
import logging
_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit ='res.partner'

    customer_no = fields.Char('Customer Number', select=True, compute='_get_customer_no', store=True)

    #Use this field definition, and remove depends on _get_customer_no
    #to avoid calculating customer_no for all customers on installation.
    #Switch back and upgrade after installation.
    #customer_no = fields.Char('Customer Number', select=True)

    @api.one
    @api.depends('ref','parent_id','parent_id.customer_no')
    def _get_customer_no(self):
        _logger.warn('_get_customer_no %s, %s' % (self.id, self.name))
        if self.parent_id:
            self.customer_no = self.parent_id.customer_no
        else:
            self.customer_no = self.ref

    @api.v7
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=10):
        if context.get('customer_no_search'):
            return self.name_get(cr, uid, self.pool.get('res.partner').search(cr, uid, [('ref', '=ilike', '%s%%' % name)])) + super(res_partner, self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)
        else:
            return super(res_partner, self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)

    @api.one
    def generate_new_customer_no(self):
        self.ref = self._generate_new_customer_no(self.customer, self.supplier)

    @api.model
    def _generate_new_customer_no(self, customer=False, supplier=False):
        if customer:
            return self.env['ir.sequence'].get('res.partner.customer.no')
        elif supplier:
            return self.env['ir.sequence'].get('res.partner.supplier.no')
        return ''

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if not (vals.get('parent_id') and vals.get('ref')) and (not int(self.env['ir.config_parameter'].get_param('sale_customer_no.company_only', '0')) or vals.get('is_company')):
            vals['ref'] = self._generate_new_customer_no(vals.get('customer'), vals.get('supplier'))
        return super(res_partner, self).create(vals)

class sale_order(models.Model):
    _inherit = 'sale.order'

    customer_no = fields.Char('Customer Number', related="partner_id.customer_no", store=True)

    @api.one
    def get_customer_no(self):
        self.partner_id.write({'ref': self.partner_id.ref })
