from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = "project.task"
    _order = "date_deadline desc, priority desc, sequence, id desc"

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def set_date_default(self):
        current_date = fields.Date.today()
        _logger.warning(f"{current_date=}")
        icp = self.env['ir.config_parameter'].sudo()
        days = icp.get_param('sale_order_deadline_task.sale_order_deadline_default', default=14)
        
        two_weeks_forward = current_date + relativedelta(days =+ int(days))
        _logger.warning(f"{two_weeks_forward=}")
        # your logic goes here
        return two_weeks_forward

    date_deadline = fields.Date(string="Deadline",default=set_date_default, required=True)
    
    
    
    # ~ @api.onchange("date_deadline")
    # ~ def _set_delivery_date(self):
        # ~ self.commitment_date = self.date_deadline

    # Calls create_event when the deadline or the assigned user on the project task is changed
    def write(self,values):
        res = super(SaleOrder,self).write(values)
        if values.get('date_deadline'):
            self.commitment_date = values.get('date_deadline')
        for record in self:
            if not record.partner_id.name:
                _logger.warning(f"{record=}")
                raise UserError(_('You can not write to a sale order that has a customer with no name'))
            if not record.partner_id.phone and not record.partner_id.mobile:
                raise UserError(_('You can not write to a sale order that has a customer with no phone and mobile number'))
        return res
    
    @api.model
    def create(self,values):
        
        res = super(SaleOrder,self).create(values)
        if not res.partner_id.name:
            raise UserError(_('You can not create a sale order with a customer that has no name'))
        if not res.partner_id.phone and not res.partner_id.mobile:
            raise UserError(_('You can not create a sale order with a customer that has no phone and mobile number'))
        if values.get('date_deadline'):
            res.commitment_date = values.get('date_deadline')
        return res
    
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    date_deadline = fields.Date(string="Deadline", related='order_id.date_deadline')
    
    def _timesheet_create_task_prepare_values(self, project):        
        res = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)
        res.update({
            'date_deadline': self.date_deadline,
        })
        amount_of_tasks = self.env['project.task'].search_count([('date_deadline' ,'=', self.date_deadline)])
        icp = self.env['ir.config_parameter'].sudo()
        deadline_max_tasks = icp.get_param('sale_order_deadline_task.deadline_max_tasks', default=10)
        if amount_of_tasks > int(deadline_max_tasks):
            raise UserError(_("You have a lot of task set for this deadline"))
                
        return res
        

