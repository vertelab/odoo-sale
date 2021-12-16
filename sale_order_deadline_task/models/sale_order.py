from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_deadline = fields.Date(string="Deadline")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    date_deadline = fields.Date(string="Deadline", related='order_id.date_deadline')

    def _timesheet_create_task_prepare_values(self, project):
        res = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)
        res.update({
            'date_deadline': self.date_deadline,
        })
        return res
