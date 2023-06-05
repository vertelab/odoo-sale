from odoo import models, fields, _, api
    

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    work_description = fields.Char(string="Work Description")
    
    def _action_confirm(self):
        res = super()._action_confirm()
        for record in self:
            for task in record.order_line.tasks_ids:
                    if not task.description:
                        task.description = task.sale_line_id.work_description
                    if not task.object_description:
                         task.object_description = task.sale_line_id.name
                    
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    work_description = fields.Char(string="Work Description")
    
    tasks_ids = fields.One2many('project.task','sale_line_id')
    
    # ~ @api.onchange('product_id')
    # ~ def product_id_change_set_work_description(self):
        # ~ for record in self: 
            # ~ if record.product_id.work_description:
                # ~ record.work_description = record.product_id.work_description
    
    # ~ def _timesheet_create_task_prepare_values(self, project):
        # ~ for record in self:
            # ~ res = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)
        
            # ~ _logger.warning(f"{record.tasks_ids=}")
            # ~ for task in record.tasks_ids:
            # ~ _logger.error(f"{self.work_description}")
                # ~ res.update({
                    # ~ 'description': self.work_description,
                    # ~ 'object_description': self.name,
                # ~ })
            # ~ _logger.error(f"{res=}")
        # ~ return res
        
        
