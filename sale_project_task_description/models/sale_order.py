from odoo import models, fields, _, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    work_description = fields.Html(string="Work Description")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _timesheet_create_task_prepare_values(self, project):
        res = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)
        res.update({
            'description': self.order_id.work_description,
            'object_description': self.name,
        })
        return res
