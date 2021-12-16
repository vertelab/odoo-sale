from odoo import models, fields, _, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    get_notified = fields.Boolean(string="Get Notified", help="Get help notified of sale orders ready to deliver")
