# -*- coding: utf-8 -*-
{
    'name': 'Elk SMS in sale order',
    'version': '1.0',
    'depends': [
        'sale',
        'sale_management',
        'sale_order_phone_number',
        'elk46_send_sms',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_sms_view.xml',
        'wizard/send_sms_wizard_views.xml',
    ],
}
