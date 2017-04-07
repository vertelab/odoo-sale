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
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit ='sale.order'
    
    parent_order_id = fields.Many2one(string='Previous Version', comodel_name='sale.order')
    child_order_ids = fields.One2many(string='Newer Versions', comodel_name='sale.order', compute='_get_child_order_ids')
    
    @api.one
    def _get_child_order_ids(self):
        child_order_ids = self.browse()
        children = self
        while children:
            children = self.search([('parent_order_id', 'in', [c.id for c in children])])
            child_order_ids |= children
        self.child_order_ids = child_order_ids
    
    @api.multi
    def copy_quotation(self):
        self.ensure_one()
        
        name = self.name.split('-')
        orders = self.search([('name', 'ilike', name[0]), ('state', '!=', 'cancel')])
        if orders:
            raise Warning(_("An active version of this order already exists: %s.") % ', '.join([o.name for o in orders]))
        version = 1
        try:
            if len(name) > 1:
                version = int(name[1]) + 1
            while True:
                if self.search([('name', '=', '%s-%s' % (name[0], version))]):
                    version += 1
                else:
                    break
            name = '%s-%s' % (name[0], version)
        except:
            raise Warning(_("Couldn't read order name and version from original order name."))
        new_order = self.copy({'name': name, 'parent_order_id': self.id})
        view_id = self.env['ir.model.data'].xmlid_lookup('sale.view_order_form')[2]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'res_id': new_order.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }
