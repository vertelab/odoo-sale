from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    hr_department_id = fields.Many2one(
        'hr.department', string="Department", related='user_id.employee_id.department_id', store=True
    )
    hr_manager_id = fields.Many2one(
        'hr.employee', string="Department Manager", related='hr_department_id.manager_id', store=True
    )
    hr_manager_user_id = fields.Many2one(
        'res.users', string="Department Manager User", related='hr_manager_id.user_id', store=True
    )