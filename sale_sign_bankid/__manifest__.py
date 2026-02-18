# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale: Sign Sale Order with BankID",
    "summary": """
        Sign Sale Order with BankID
    """,
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/vertel/odoo-sale",
    "depends": ['sign_bankid', 'sale'],
    "data": [
        'views/sale_order_view.xml',
        'views/sale_portal_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [

        ],
    }

}
