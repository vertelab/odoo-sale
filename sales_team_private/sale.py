# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2019 Vertel AB (<http://vertel.se>).
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

    
class ResPartner(models.Model):
    _inherit = "res.partner"
    
    def _default_sales_team_ids(self):
        # ~ _logger.warn('\n\n_default_sales_team_ids\n%s\n' % self.env.context)
        return self.env.user.sale_team_id
    
    sales_team_ids = fields.Many2many(comodel_name='crm.team', string='Sales Teams', default=_default_sales_team_ids)
    sales_team_restrict = fields.Boolean(string='Sales Team Restrict', compute='_sales_team_restrict', search='_search_sales_team_restrict', help="Dummy field to restrict resources depending on user sales team.")
    # TODO: Move CV field to some other module
    cv_text = fields.Text(string='CV')
    
    def _sales_team_restrict(self):
        pass
    
    def _search_sales_team_restrict(self, op, value):
        return self.get_sales_team_restrict_domain()
    
    def get_sales_team_restrict_domain(self, field_name='commercial_partner_id.sales_team_ids'):
        """Calculate which resources should be allowed depending on user groups and sales team.
        
        :param field_name: The name of the sales team field for the given model.
        :returns: A search domain expressing the users security restrictions.
        """
        # Seems like this is run as admin. Fetch user from uid.
        user = self.env['res.users'].browse(self.env.context.get('uid'))
        if not user:
            return []
        # ~ _logger.warn('\n\nget_sales_team_restrict_domain\n%s\n%s\n' % (self.env.context, self.env.user))
        if user._is_admin():
            # Don't apply restriction to admin.
            # ~ _logger.warn('\n\nadmin\n')
            return []
        if not user._has_group('base.group_user'):
            # Only apply this restriction to internal users.
            # ~ _logger.warn('\n\nnot employee\n')
            return []
        if user._has_group('sales_team_private.group_sale_all_salesteams'):
            # This user has cross team access.
            # ~ _logger.warn('\n\ncross team access\n')
            return []
        # Restrict to own sales teams, or no sales team.
        team_ids = [d['id'] for d in self.env['crm.team'].search_read(['|', ('user_id', '=', user.id), ('member_ids', '=', user.id)], ['id'])]
        # ~ if user.sale_team_id:
            # ~ team_ids.append(user.sale_team_id.id)
        # ~ _logger.warn('\n\nteam_ids: %s\n' % team_ids)
        if team_ids:
            return ['|', (field_name, '=', False), (field_name, 'in', team_ids)]
        return [(field_name, '=', False)]

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    sales_team_restrict = fields.Boolean(string='Sales Team Restrict', compute='_sales_team_restrict', search='_search_sales_team_restrict', help="Dummy field to restrict resources depending on user sales team.")
    
    def _sales_team_restrict(self):
        pass
    
    def _search_sales_team_restrict(self, op, value):
        return self.env['res.partner'].get_sales_team_restrict_domain('partner_id.sales_team_ids')

class CrmLead(models.Model):
    _inherit = "crm.lead"
    
    sales_team_restrict = fields.Boolean(string='Sales Team Restrict', compute='_sales_team_restrict', search='_search_sales_team_restrict', help="Dummy field to restrict resources depending on user sales team.")
    
    def _sales_team_restrict(self):
        pass
    
    def _search_sales_team_restrict(self, op, value):
        return self.env['res.partner'].get_sales_team_restrict_domain('team_id')
