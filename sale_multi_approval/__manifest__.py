# -*- coding: utf-8 -*-
{
    'name': "sale_multi_approval",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'rest_base', 'rest_signport', 'res_user_groups_skogsstyrelsen', "partner_ssn"],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/sale_approval_view.xml',
        'views/sale_inherited.xml',
        'data/data.xml',
    ],
}
