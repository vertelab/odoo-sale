# -*- coding: utf-8 -*-
{
    'name': "sale_multi_approval",

    'summary': """
        Adds multi aproval functionality using bankid for sale orders""",

    'description': """
        Adds multi aproval functionality using bankid for sale orders
    """,

    'author': "Vertel AB",
    'website': "www.vertel.se",

    # Categories can be used to filter modules in modules listing
    'category': 'sale',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'rest_base', 'rest_signport', 'res_user_groups_skogsstyrelsen', "partner_ssn"],

    # always loaded
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
    ],
}
