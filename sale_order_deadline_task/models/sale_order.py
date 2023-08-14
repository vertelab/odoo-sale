from calendar import c
from itertools import count
from typing import Counter
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.models import expression
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = "project.task"
    _order = "date_deadline desc, priority desc, sequence, id desc"


class ProjectTaskDeadlineOverview(models.Model):
    _name = "project.task.deadline.overview"
    _description = "Project Task Deadline Overview"
    _order = "date desc"


    date = fields.Char(string='Date')
    count = fields.Integer(string='Count')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    max_tasks = fields.Integer(string="Max Tasks")

    

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

    task_deadline_overview = fields.One2many('project.task.deadline.overview', 'sale_order_id', string='Task Overview', compute='_compute_task_deadline_overview')

    @api.onchange('date_deadline')
    def _compute_task_deadline_overview(self):
        icp = self.env['ir.config_parameter'].sudo()
        max_tasks = icp.get_param('sale_order_deadline_task.deadline_max_tasks', default=10)
        for record in self:
            record.task_deadline_overview = False
            if record.date_deadline:
                deadline_overview_count = self.env['ir.config_parameter'].sudo().get_param('sale_order_deadline_task.deadline_overview_count', default=5)
                date_domain = [('date_deadline', '=', record.date_deadline)]
                for rcount in range(1, int(deadline_overview_count)):
                    date_domain = expression.OR([date_domain, [('date_deadline', '=', record.date_deadline + relativedelta(days=+rcount))]])
                    
                task_ids = self.env['project.task'].search(date_domain)
                if task_ids:
                    for date, count in Counter(task_ids.mapped('date_deadline')).items():
                        _logger.warning(f"{date}: {count}")
                        
                    record.task_deadline_overview.create({
                        'max_tasks':max_tasks,
                        'date': date,
                        'count': count,
                        'sale_order_id': record.id
                    } for date, count in Counter(task_ids.mapped('date_deadline')).items())
                else:
                    record.task_deadline_overview = False
                    
            else:
                record.task_deadline_overview = False

    
    
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
            #if not record.partner_id.phone and not record.partner_id.mobile:
            #    raise UserError(_('You can not write to a sale order that has a customer with no phone and mobile number'))
        return res
    
    @api.model
    def create(self,values):
        
        res = super(SaleOrder,self).create(values)
        if not res.partner_id.name:
            raise UserError(_('You can not create a sale order with a customer that has no name'))
        #if not res.partner_id.phone and not res.partner_id.mobile:
        #    raise UserError(_('You can not create a sale order with a customer that has no phone and mobile number'))
        if values.get('date_deadline'):
            res.commitment_date = values.get('date_deadline')
        return res
        
        
    def _action_confirm(self):
        res = super()._action_confirm()
        
        icp = self.env['ir.config_parameter'].sudo()
        deadline_max_tasks = icp.get_param('sale_order_deadline_task.deadline_max_tasks', default=10)
        
        for record in self:
            _logger.warning(f"{record=}")
            for task in record.tasks_ids:
                    if not task.date_deadline:
                        task.date_deadline = task.sale_line_id.date_deadline
                    all_tasks_with_same_deadline = self.env["project.task"].search([("date_deadline","=",task.date_deadline)])
                    if len(all_tasks_with_same_deadline) > int(deadline_max_tasks):
                        raise UserError(_('You have exceeded the number of allowed tasks. (%s)\nKindly change deadline before confirming again.'% str(deadline_max_tasks)))
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





       


