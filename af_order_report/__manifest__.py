# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "AF Order Report",
    "version": "12.0.1.3",
    "author": "Vertel AB",
    "license": "AGPL-3",
    "website": "https://vertel.se/",
    "category": "Tools",
    "description": """
	 v12.0.1.3 AFC-1139 - Mail template for KVL
    """,
    "depends": ["sale"],
    "external_dependencies": [],
    "data": [
        'views/sale_order_view.xml',

        'reports/assigned_coach_report.xml',
        'reports/first_meeting_report.xml',

        'data/mail_template.xml',

    ],
    "application": True,
    "installable": True,
}
