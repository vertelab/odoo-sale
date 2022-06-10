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
        return res
    
    def _timesheet_service_generation(self):
        """ For service lines, create the task or the project. If already exists, it simply links
            the existing one to the line.
            Note: If the SO was confirmed, cancelled, set to draft then confirmed, avoid creating a
            new project/task. This explains the searches on 'sale_line_id' on project/task. This also
            implied if so line of generated task has been modified, we may regenerate it.
        """
        before_create_amount_of_tasks = self.env['project.task'].search_count([('date_deadline' ,'=', self.order_id.date_deadline)])
        already_created_tasks_amount = 0
        if self.task_id:
            already_created_tasks_amount = len(self.task_id)
        so_line_task_global_project = self.filtered(lambda sol: sol.is_service and sol.product_id.service_tracking == 'task_global_project')
        so_line_new_project = self.filtered(lambda sol: sol.is_service and sol.product_id.service_tracking in ['project_only', 'task_in_project'])

        # search so lines from SO of current so lines having their project generated, in order to check if the current one can
        # create its own project, or reuse the one of its order.
        map_so_project = {}
        if so_line_new_project:
            order_ids = self.mapped('order_id').ids
            so_lines_with_project = self.search([('order_id', 'in', order_ids), ('project_id', '!=', False), ('product_id.service_tracking', 'in', ['project_only', 'task_in_project']), ('product_id.project_template_id', '=', False)])
            map_so_project = {sol.order_id.id: sol.project_id for sol in so_lines_with_project}
            so_lines_with_project_templates = self.search([('order_id', 'in', order_ids), ('project_id', '!=', False), ('product_id.service_tracking', 'in', ['project_only', 'task_in_project']), ('product_id.project_template_id', '!=', False)])
            map_so_project_templates = {(sol.order_id.id, sol.product_id.project_template_id.id): sol.project_id for sol in so_lines_with_project_templates}

        # search the global project of current SO lines, in which create their task
        map_sol_project = {}
        if so_line_task_global_project:
            map_sol_project = {sol.id: sol.product_id.with_company(sol.company_id).project_id for sol in so_line_task_global_project}

        def _can_create_project(sol):
            if not sol.project_id:
                if sol.product_id.project_template_id:
                    return (sol.order_id.id, sol.product_id.project_template_id.id) not in map_so_project_templates
                elif sol.order_id.id not in map_so_project:
                    return True
            return False

        def _determine_project(so_line):
            """Determine the project for this sale order line.
            Rules are different based on the service_tracking:

            - 'project_only': the project_id can only come from the sale order line itself
            - 'task_in_project': the project_id comes from the sale order line only if no project_id was configured
              on the parent sale order"""

            if so_line.product_id.service_tracking == 'project_only':
                return so_line.project_id
            elif so_line.product_id.service_tracking == 'task_in_project':
                return so_line.order_id.project_id or so_line.project_id

            return False

        # task_global_project: create task in global project
        for so_line in so_line_task_global_project:
            if not so_line.task_id:
                if map_sol_project.get(so_line.id):
                    so_line._timesheet_create_task(project=map_sol_project[so_line.id])

        # project_only, task_in_project: create a new project, based or not on a template (1 per SO). May be create a task too.
        # if 'task_in_project' and project_id configured on SO, use that one instead
        for so_line in so_line_new_project:
            project = _determine_project(so_line)
            if not project and _can_create_project(so_line):
                project = so_line._timesheet_create_project()
                if so_line.product_id.project_template_id:
                    map_so_project_templates[(so_line.order_id.id, so_line.product_id.project_template_id.id)] = project
                else:
                    map_so_project[so_line.order_id.id] = project
            elif not project:
                # Attach subsequent SO lines to the created project
                so_line.project_id = (
                    map_so_project_templates.get((so_line.order_id.id, so_line.product_id.project_template_id.id))
                    or map_so_project.get(so_line.order_id.id)
                )
            if so_line.product_id.service_tracking == 'task_in_project':
                if not project:
                    if so_line.product_id.project_template_id:
                        project = map_so_project_templates[(so_line.order_id.id, so_line.product_id.project_template_id.id)]
                    else:
                        project = map_so_project[so_line.order_id.id]
                if not so_line.task_id:
                    so_line._timesheet_create_task(project=project)
        # ~ after_create_amount_of_tasks = self.env['project.task'].search_count([('date_deadline' ,'=', self.order_id.date_deadline)])
        # ~ _logger.warning(f"{after_create_amount_of_tasks=}")
        # ~ _logger.warning(f"{self.task_id}")
        _logger.warning(f"{len(self.task_id)}")
        icp = self.env['ir.config_parameter'].sudo()
        created_tasks_amount = len(self.task_id) - already_created_tasks_amount
        total_tasks = created_tasks_amount + before_create_amount_of_tasks
        deadline_max_tasks = icp.get_param('sale_order_deadline_task.deadline_max_tasks', default=10)
        if total_tasks > int(deadline_max_tasks):
            # ~ raise UserError(_(f"When confirming this sale order you have tried to create {created_tasks_amount} tasks.\nThere were already {before_create_amount_of_tasks} with the deadline {self.order_id.date_deadline}.\nThis will result in {total_tasks} tasks with the same deadline, which is more than the max allowed of {deadline_max_tasks}.\nKindly change deadline before confirming."))
            raise UserError(_('When confirming this sale order you have tried to create %s tasks.\nThere were already %s  with the deadline %s .\nThis will result in %s  tasks with the same deadline, which is more than the max allowed of %s.\nKindly change deadline before confirming.'% (str(created_tasks_amount), str(before_create_amount_of_tasks), str(self.order_id.date_deadline),str(total_tasks), str(deadline_max_tasks))))
            
        # ~ _logger.warn(_("Couldn't match line (id %s) against existing transfer item!\nlines:%s\ntransfer items:%s") % (line['id'], lines, wizard.item_ids.read()))
