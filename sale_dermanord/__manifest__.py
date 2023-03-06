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
    'name': 'Sale: Dermanord',
    'version': '14.0.0.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Special order imports for Dermanord AB.',
    'category': 'Sales',
    'description': """
Special order imports for Dermanord AB
======================================
* Fina mig i Hedemora AB (pdf)
* Lyko Online AB (Excel)
* SKINCITY SWEDEN AB (pdf)
* Isaksen & CO AS (Excel)
* Nordic Web Trading AB (Excel)
* Eckerö Group - Rederiaktiebolaget Eckerö (Birka) (Text)
* Tailwide AB (Narutligt snygg) (Url)

""",
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-sale/sale_dermanord',

    'depends': ['sale', 'sale_management'],
    'external_dependencies': {
        'python': ['xlrd', 'pdfminer', 'unicodecsv'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/order_import_view.xml',
    ],
    'application': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
