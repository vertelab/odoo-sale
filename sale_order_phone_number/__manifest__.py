# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Order Phone Number',
    'version': '14.0.0.0.1',
    'category': 'Sales',
    'summary': 'Sale Order Phone Number',
    'description': """
This module adds phone number to sale order.
    """,
    'depends': ['sale'],
    'data': [
        'views/sale_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
