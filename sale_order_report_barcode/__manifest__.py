# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Order Report Barcode',
    'version': '14.0.0.0.1',
    'category': 'Sales/Sales',
    'summary': 'Sale Order Report Barcode',
    'description': """
        14.0.0.0.1 - Added barcode to sale order report.
    """,
    'depends': ['sale_management'],
    'data': [
        'views/sale_report_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
