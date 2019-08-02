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
    
    sales_team_restrict = fields.Boolean(string='Sales Team Restrict', compute='_sales_team_restrict', search='_search_sales_team_restrict', help="Dummy field to restrict resources depending on user sales team.")
    
    def _sales_team_restrict(self):
	pass
    
    def _search_sales_team_restrict(self):
	"""Calculate which resources should be allowed depending on user groups and sales team."""
	if not self.env.user._has_group('base.group_user'):
	    # Only apply this restriction to internal users.
	    return []
	if self.env.user._has_group('sales_team_private.group_sale_all_salesteams'):
	    # This user has cross team access.
	    return []
	# Restrict to own sales team, or no sales team.
	team_id = self.env.user.team_id and self.env.user.team_id.id
	return ['|', ('team_id', '=', False), ('team_id', '=', team_id)]
	
