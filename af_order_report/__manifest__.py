# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "AF Order Report",
    "version": "12.0.1.3",
    "summary": "AF Order Report",
    "author": "Vertel AB",
    "license": "AGPL-3",
    "website": "https://vertel.se/",
    "category": "Tools",
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
