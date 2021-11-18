# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Order Ready to Deliver',
    'version': '1.1',
    'category': 'Sales/Sales',
    'summary': 'Sale Order Ready to Deliver',
    'description': """
        This module adds ready to deliver to project and sale order.
    """,
    'depends': ['sale', 'project'],
    'data': [
        'views/project_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
