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
    
    def _default_sales_team_id(self):
        # ~ _logger.warn('\n\n_default_sales_team_id\n%s\n' % self.env.context)
        res = self.env.user.sale_team_id
        if not res:
            res = selv.env['crm.team'].search([('user_id','=',self.env.user.id)], limit=1)
        return res
    
    sales_team_id = fields.Many2one(comodel_name='crm.team', string='Sales Team', default=_default_sales_team_id)
    sales_team_restrict = fields.Boolean(string='Sales Team Restrict', compute='_sales_team_restrict', search='_search_sales_team_restrict', help="Dummy field to restrict resources depending on user sales team.")
    
    def _sales_team_restrict(self):
        # ~ _logger.warn('%s._sales_team_restrict()' % self)
        pass
    
    @api.model
    def _search_sales_team_restrict(self, op, value):
        # ~ _logger.warn('%s._search_sales_team_restrict()' % self)
        domain = self.get_sales_team_restrict_domain(('sales_team_id', 'commercial_partner_id.sales_team_id'))
        if domain:
            domain.insert(1, '&')
            domain.insert(2, ('commercial_partner_id', '=', False))
        # ~ _logger.warn(domain)
        # ~ _logger.warn(self.search(domain))
        #[
        #    '|',
        #        '&',
        #            ('commercial_partner_id', '=', False),
        #            '|',
        #                ('sales_team_id', '=', False),
        #                ('sales_team_id', 'in', [1, 2, 3]),
        #        '|',
        #            ('commercial_partner_id.sales_team_id', '=', False),
        #            ('commercial_partner_id.sales_team_id', 'in', [1, 2, 3])]
        return domain
    
    @api.model
    def get_sales_team_restrict_domain(self, field_name=('sales_team_id',), join_op='|'):
        """Calculate which resources should be allowed depending on user groups and sales team.
        
        [
            join_op,
                '|',
                    (field_name_1, '=', False),
                    (field_name_1, 'in', [1, 2, 3]),
                '|',
                    (field_name_2, '=', False),
                    (field_name_2, 'in', [1, 2, 3])]
        
        :param field_name: The name of the sales team field for the given model. Can be a list or tuple if several fields are to be used.
        :returns: A search domain expressing the users security restrictions.
        """
        # Seems like this is run as admin. Fetch user from uid.
        assert join_op in ('|', '&'), "get_sales_team_restrict_domain: '%s' is not a valid operator!" % join_op
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
        domain = []
        if type(field_name) not in (list, tuple):
            field_name = (field_name,)
        for field in field_name:
            if domain:
                domain.insert(0, '|')
            if team_ids:
                domain.extend(('|', (field, '=', False), (field, 'in', team_ids)))
            else:
                domain.append((field, '=', False))
        # ~ _logger.warn('domain: %s' % domain)
        return domain
    
    @api.model
    def create(self, vals):
        # ~ _logger.warn('%s.create(%s)' % (self, vals))
        return super().create(vals)
    
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    sales_team_restrict = fields.Boolean(string='Sales Team Restrict', compute='_sales_team_restrict', search='_search_sales_team_restrict', help="Dummy field to restrict resources depending on user sales team.")
    
    @api.multi
    def _sales_team_restrict(self):
        # ~ _logger.warn('%s._sales_team_restrict()' % self)
        # ~ allowed = self.search([('id', 'in', self.ids), ('sales_team_restrict', '=', True)])
        # ~ for record in self:
            # ~ if record in allowed:
                # ~ record.sales_team_restrict = True
        pass
    
    @api.model
    def _search_sales_team_restrict(self, op, value):
        return self.env['res.partner'].get_sales_team_restrict_domain(('team_id', 'partner_id.sales_team_id'), '&')

class CrmLead(models.Model):
    _inherit = "crm.lead"
    
    sales_team_restrict = fields.Boolean(string='Sales Team Restrict', compute='_sales_team_restrict', search='_search_sales_team_restrict', help="Dummy field to restrict resources depending on user sales team.")
    
    def _sales_team_restrict(self):
        pass
    
    @api.model
    def _search_sales_team_restrict(self, op, value):
        return self.env['res.partner'].get_sales_team_restrict_domain('team_id')
