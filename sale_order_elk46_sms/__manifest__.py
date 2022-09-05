# -*- coding: utf-8 -*-
{
    'name': 'Elk SMS in sale order',
    'version': '1.0',
    'depends': [
        'sale',
        
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/send_sms_wizard_views.xml',
        'views/sale_order_sms_view.xml',
    ],
}
