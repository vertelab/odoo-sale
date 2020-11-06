from odoo import fields, api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    hr_employee = fields.Many2one('hr.employee', string="HR")
