# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Hide Quotation Price Details',
    'version': '1.1',
    'category': 'Sales/Sales',
    'summary': 'Hide Quotation Price Details',
    'description': """
This module hide price details for quotations.
    """,
    'depends': ['sale'],
    'data': [
        'report/sale_report_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
