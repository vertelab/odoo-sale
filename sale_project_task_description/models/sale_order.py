from odoo import models, fields, _, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    work_description = fields.Html(string="Work Description")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _timesheet_create_task(self, project):
        """ Generate task for the given so line, and link it.
            :param project: record of project.project in which the task should be created
            :return task: record of the created task
        """
        values = self._timesheet_create_task_prepare_values(project)
        values['object_description'] = self.name
        values['description'] = self.order_id.work_description
        task = self.env['project.task'].sudo().create(values)
        self.write({'task_id': task.id})
        # post message on task
        task_msg = _("This task has been created from: <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a> (%s)") \
                   % (self.order_id.id, self.order_id.name, self.product_id.name)
        task.message_post(body=task_msg)
        return task
