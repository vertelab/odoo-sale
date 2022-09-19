# -*- coding: utf-8 -*-
# License: AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    'name': 'Sales: Controls VAT on Sales Report',
    'version': '14.0.0.0.1',
    'category': 'Sales/Sales',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-sale/sale_delivery_vat_report',
    'license': 'LGPL-3',
    'summary': 'Controls VAT on Sales Report',
    'depends': [
        'base_company_fiscal_position',
        'sale'
    ],
    'data': [
        'report/sale_report_templates.xml',
    ],
    'installable': True,
}
