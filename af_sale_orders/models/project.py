from odoo import models, fields, api, _
from odoo.exceptions import Warning

class ProjectProject(models.Model):

    _inherit = 'project.project'

    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    sale_order_id = fields.Many2one('sale.order')

class ProjectTask(models.Model):

    _inherit = 'project.task'
    _rec_name = 'task_name_number'
    _order = "sequence, priority desc, id desc"

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
        to_do_stage_id = self.env.ref('project.project_stage_0').id
        if self.parent_task_id:
            self.color = self.parent_task_id.color
            self.stage_id = to_do_stage_id
        else:
            self.color = 0

    def update_task_name(self):
        sub_tasks_list = []
        for task in self:
            if task.id not in sub_tasks_list:
                if task.parent_task_id:
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
        if 'from_sale_order' not in self._context and not vals.get('optional_task') and \
                not vals.get('parent_task_id') and res.project_id and res.project_id.sale_order_id:
            raise Warning(_("You can't create Parent Task!"))
        todo_stage = self.env.ref('project.project_stage_0')
        if vals.get('parent_task_id'):
            res.stage_id = todo_stage.id
            parent_task = self.env['project.task'].browse(vals.get('parent_task_id'))
            res.color = parent_task.color
            sub_tasks = self.search([('parent_task_id', '=', parent_task.id), ('id', '!=', res.id)])
            sub_tasks_len = len(sub_tasks)
            if parent_task.task_number:
                if not sub_tasks and res.project_id:
                    other_tasks = self.env['project.task'].search([('sequence', '>', parent_task.sequence),
                                                ('project_id', '=', parent_task.project_id.id),
                                                                   ('id', '!=', res.id)], order='sequence')
                    for o_task in other_tasks:
                        o_task.sequence = o_task.sequence + 1
                    res.sequence = parent_task.sequence + 1
                elif sub_tasks and res.project_id:
                    other_tasks = self.env['project.task'].search([('sequence', '>', parent_task.sequence),
                                                        ('project_id', '=', parent_task.project_id.id),
                                                        ('id', '!=', res.id), '|', ('parent_task_id', '=', False),
                                                        ('parent_task_id', '!=', parent_task.id)], order='sequence')
                    for o_task in other_tasks:
                        o_task.sequence = o_task.sequence + 1
                    res.sequence = parent_task.sequence + sub_tasks_len + 1
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
        done_stage = self.env.ref('project.project_stage_2')
        todo_stage = self.env.ref('project.project_stage_0')
        for task in self:
            if task.optional_task and task.stage_id and task.stage_id.id == todo_stage.id:
                raise Warning(_("Can not move Optional task to Todo stage!"))
            if vals.get('stage_id'):
                if task.stage_id and task.stage_id.name == 'Done':
                    subtasks = self.search([('parent_task_id', '=', task.id)])
                    for sub_task in subtasks:
                        if not sub_task.stage_id.id == done_stage.id:
                            raise Warning(_("You can't move this task to Done as its subtask %s is not Done" % sub_task.name))
                        sub_task.stage_id = done_stage.id
            if vals.get('name') and task.parent_task_id and not vals.get('parent_task_id'):
                number = task.task_name_number.split(' ')
                if len(number) > 1:
                    number = number[0]
                    task.task_name_number = number + ' ' + task.name
            if vals.get('parent_task_id'):
                parent_task = task_obj.browse(vals.get('parent_task_id'))
                task.color =parent_task.color
                sub_tasks = self.search([('parent_task_id', '=', parent_task.id), ('id', '!=', task.id)])
                sub_tasks_len = len(sub_tasks)
                if parent_task.task_number:
                    if not sub_tasks and task.project_id:
                        other_tasks = self.env['project.task'].search([('sequence', '>', parent_task.sequence),
                                                ('id', '!=', task.id),('project_id', '=', parent_task.project_id.id)],
                                                                       order='sequence')
                        for o_task in other_tasks:
                            o_task.sequence = o_task.sequence + 1
                        task.sequence = parent_task.sequence + 1
                    elif sub_tasks and task.project_id:
                        other_tasks = self.env['project.task'].search([('sequence', '>', parent_task.sequence),
                                                                       ('id', '!=', task.id),
                                                                       ('project_id', '=', parent_task.project_id.id),
                                                                       '|', ('parent_task_id', '=', False),
                                                                       ('parent_task_id', '!=', parent_task.id)],
                                                                      order='sequence')
                        for o_task in other_tasks:
                            o_task.sequence = o_task.sequence + 1
                        task.sequence = parent_task.sequence + sub_tasks_len + 1

                    task.task_name_number = parent_task.task_number + '.' + str(sub_tasks_len + 1) + ' ' + task.name
                else:
                    task.task_name_number = task.name
            if vals.get('task_number'):
                task.task_name_number = task.task_number + ' ' + task.name
        return res

    @api.multi
    def unlink(self):
        done_stage = self.env.ref('project.project_stage_2')
        for task in self:
            subtasks = self.search([('parent_task_id', '=', task.id)])
            if subtasks:
                raise Warning("You can't remove Parent Task!")
            if task.required_task:
                raise Warning(_("You can't remove this task as this is required task!"))
            if task.parent_task_id and task.stage_id and task.parent_task_id.stage_id and \
                    (task.stage_id.id == done_stage.id or task.parent_task_id.stage_id.id == done_stage.id):
                raise Warning(_("You can't remove task which is Done or Parent Task is Done!"))
        return super(ProjectTask, self).unlink()

class TaskStages(models.Model):
    _inherit = 'project.task.type'

    @api.multi
    def name_get(self):
        vals = []
        context = self._context
        for record in self:
            if 'search_default_project_id' in context:
                name = record.name
                if record.description:
                    name += ' - '
                    name += record.description
            else:
                name = record.name
            vals.append((record.id, name))
        return vals