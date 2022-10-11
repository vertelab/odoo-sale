# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2021- Vertel AB (<https://vertel.se>).
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
    'name': 'Sale Order Contract Ongoing',
    'version': '14.0.0.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Use a contract to invoice the same Sale order accoding to the contract',
    'category': 'Marketing',
    'description': """
        Adds a new function to a contract.
        Create a sale order and to invoice the same sale order according to the contract.
    """,
    #'sequence': '1'
    #'images': ['images/main_screenshot.png']
    # Third part projects: https://github.com/OCA/contract,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'depends': ['sale', 'project','contract', 'hr', 'hr_timesheet', 'sale_timesheet','contract_sale_generation' ],
    'data': [
        'views/contract.xml',
        #'views/hr_employee_view.xml',
        #'views/analytic_line.xml',
    ],
    'installable': True,
    'auto_install': False,
}
