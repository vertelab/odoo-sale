# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale: Sign Sale Order",
    "summary": """
        Sign Sale Order with Multiple Providers
    """,
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://vertel.se/apps/odoo-sale/sale_vrtl_sign",
    "depends": ['sign_vrtl', 'sale'],
    "data": [
        'views/sale_order_view.xml',
    ],
    'assets': {
        'web.assets_backend': [

        ],
    }

}
