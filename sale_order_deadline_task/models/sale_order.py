from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_deadline = fields.Date(string="Deadline")
    
    # ~ @api.onchange("date_deadline")
    # ~ def _set_delivery_date(self):
        # ~ self.commitment_date = self.date_deadline

    # Calls create_event when the deadline or the assigned user on the project task is changed
    def write(self,values):
        res = super(SaleOrder,self).write(values)
        if values.get('date_deadline'):
            self.commitment_date = values.get('date_deadline')
        return res
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    date_deadline = fields.Date(string="Deadline", related='order_id.date_deadline')

    def _timesheet_create_task_prepare_values(self, project):
        res = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)
        res.update({
            'date_deadline': self.date_deadline,
        })
        return res
        

