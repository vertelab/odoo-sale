from odoo import models, fields, api, _
from odoo.exceptions import Warning

class ProjectProject(models.Model):

    _inherit = 'project.project'

    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")

class ProjectTask(models.Model):

    _inherit = 'project.task'
    _rec_name = 'task_name_number'
    _order = "task_number, priority desc, sequence, id desc"

    task_number = fields.Char("Main Task number")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    task_name_number = fields.Char("Task name")
    parent_task_id = fields.Many2one('project.task', "Parent Task")
    required_task = fields.Boolean("Required Task", copy=False)
    optional_task = fields.Boolean("Optional Task", copy=False)
    instruction = fields.Text("Instruction")

    @api.onchange('parent_task_id')
    def onchange_parent_task_id(self):
        if self.parent_task_id:
            self.color = 10
        else:
            self.color = 0

    def update_task_name(self):
        sub_tasks_list = []
        for task in self:
            if task.id not in sub_tasks_list:
                if task.parent_task_id:
                    task.color = 10
                    parent_task = task.parent_task_id
                    sub_tasks = self.search([('parent_task_id', '=', parent_task.id)])
                    if parent_task.task_number:
                        counter = 0
                        for sub_task in sub_tasks:
                            sub_task.task_name_number = parent_task.task_number + '.' + str(counter + 1) + ' ' + sub_task.name
                            counter += 1
                            sub_tasks_list.append(task.id)
                    else:
                        task.task_name_number = task.name
                elif task.task_number:
                    task.task_name_number = task.task_number + ' ' + task.name
                else:
                    task.task_name_number = task.name

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        if vals.get('parent_task_id'):
            res.color = 10
            parent_task = self.env['project.task'].browse(vals.get('parent_task_id'))
            sub_tasks = self.search([('parent_task_id', '=', parent_task.id), ('id', '!=', res.id)])
            sub_tasks_len = len(sub_tasks)
            if parent_task.task_number:
                res.task_name_number = parent_task.task_number + '.' + str(sub_tasks_len + 1) + ' ' + res.name
            else:
                res.task_name_number = res.name
        elif vals.get('task_number'):
            res.task_name_number = str(vals.get('task_number')) + ' ' + res.name
        else:
            res.task_name_number = res.name
        return res

    @api.multi
    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        task_obj = self.env['project.task']
        for task in self:
            if vals.get('name') and task.parent_task_id and not vals.get('parent_task_id'):
                number = task.task_name_number.split(' ')
                if len(number) > 1:
                    number = number[0]
                    task.task_name_number = number + ' ' + task.name
            if vals.get('parent_task_id'):
                task.color = 10
                parent_task = task_obj.browse(vals.get('parent_task_id'))
                sub_tasks = self.search([('parent_task_id', '=', parent_task.id), ('id', '!=', task.id)])
                sub_tasks_len = len(sub_tasks)
                if parent_task.task_number:
                    task.task_name_number = parent_task.task_number + '.' + str(sub_tasks_len + 1) + ' ' + task.name
                else:
                    task.task_name_number = task.name
            if vals.get('task_number'):
                task.task_name_number = task.task_number + ' ' + task.name
        return res

    @api.multi
    def unlink(self):
        for task in self:
            if task.required_task:
                raise Warning(_("You can't remove this task as this is required task!"))
        return super(ProjectTask, self).unlink()