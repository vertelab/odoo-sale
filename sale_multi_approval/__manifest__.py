# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Sale: Multi Approval',
    'version': '14.0.0.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Adds multi approval functionality using bank-id for sale orders.',
    'category': 'Sales',
    'description': """
    Adds multi approval functionality using bank-id for sale orders.
    """,
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-sale/sale_multi_approval',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-sale',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'rest_base', 'rest_signport', 'res_user_groups_skogsstyrelsen', "partner_ssn"],

    # 1. always loaded
    # sale_multi_approval:
    # This module depends on a third party project.
    # git clone -b 14.0 git@github.com:vertelab/odoo-rest.git
    # 2. sale_multi_approval:
    # This module depends on a third party project.
    # git clone -b 14.0 git@git.vertel.se:vertelab/odooext-skogsstyrelsen.git
    'data': [
        'data/data.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/sale_approval_view.xml',
        'views/sale_inherited.xml',
        'views/templates.xml',
        'views/sale_approval_view.xml',
        'views/sale_inherited.xml',
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/form_buttons.xml'
    ]
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
