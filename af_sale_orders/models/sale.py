from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        carreer_product_id = self.env.ref('af_sale_orders.kvd_01').id
        is_carreer = False
        for line in self.order_line:
            if line.product_id and line.product_id.id == carreer_product_id:
                is_carreer = True
        to_do_stage_id = self.env.ref('project.project_stage_0').id
        optional_stage_id = self.env.ref('af_sale_orders.project_optional_stage').id
        stage_ids = [self.env.ref('project.project_stage_0'), self.env.ref('project.project_stage_2'),
                     self.env.ref('af_sale_orders.project_optional_stage')]
        if is_carreer:
            project = self.env['project.project'].create({
                'name': self.partner_id.name
            })
            project.sale_order_id = self.id
            for stage in stage_ids:
                stage.project_ids = [(4, project.id)]
            task_obj = self.env['project.task']
            task_obj.with_context(from_sale_order=True).create({
                'name': "Task1",
                'project_id': project.id,
                'task_number': 1,
                'stage_id': to_do_stage_id,
                'required_task': True,
                'color': 1,
                'instruction': 'Instruction 1',
                'sequence': 1
            })
            task_obj.with_context(from_sale_order=True).create({
                'name': "Task2",
                'project_id': project.id,
                'task_number': 2,
                'stage_id': to_do_stage_id,
                'required_task': True,
                'color': 2,
                'instruction': 'Instruction 2',
                'sequence': 2
            })
            task_obj.with_context(from_sale_order=True).create({
                'name': "Task3",
                'project_id': project.id,
                'task_number': 3,
                'stage_id': to_do_stage_id,
                'required_task': True,
                'color': 3,
                'instruction': 'Instruction 3',
                'sequence': 3
            })
            task_obj.with_context(from_sale_order=True).create({
                'name': "Task4",
                'project_id': project.id,
                'task_number': 4,
                'stage_id': to_do_stage_id,
                'required_task': True,
                'color': 4,
                'instruction': 'Instruction 4',
                'sequence': 4
            })
            task_obj.with_context(from_sale_order=True).create({
                'name': "Task5",
                'project_id': project.id,
                'task_number': 5,
                'stage_id': to_do_stage_id,
                'required_task': True,
                'color': 5,
                'instruction': 'Instruction 5',
                'sequence': 5
            })
            task_obj.with_context(from_sale_order=True).create({
                'name': "Task6",
                'project_id': project.id,
                'task_number': 6,
                'stage_id': to_do_stage_id,
                'required_task': True,
                'color': 6,
                'instruction': 'Instruction 6',
                'sequence': 6
            })
            task_obj.with_context(from_sale_order=True).create({
                'name': "Task7",
                'project_id': project.id,
                'task_number': 7,
                'stage_id': to_do_stage_id,
                'required_task': True,
                'color': 7,
                'instruction': 'Instruction 7',
                'sequence': 7
            })
            task_obj.with_context(from_sale_order=True).create({
                'name': "Task8",
                'project_id': project.id,
                'task_number': 8,
                'stage_id': to_do_stage_id,
                'required_task': True,
                'color': 8,
                'instruction': 'Instruction 8',
                'sequence': 8
            })
            task_obj.with_context(from_sale_order=True).create({
                'name': "Optional-Task1",
                'project_id': project.id,
                'task_number': 1,
                'stage_id': optional_stage_id,
                'optional_task': True,
                'color': 11,
                'instruction': 'Instruction 1',
                'sequence': 9
            })
            task_obj.with_context(from_sale_order=True).create({
                'name': "Optional-Task2",
                'project_id': project.id,
                'task_number': 2,
                'stage_id': optional_stage_id,
                'optional_task': True,
                'color': 11,
                'instruction': 'Instruction 3',
                'sequence': 10
            })
            task_obj.with_context(from_sale_order=True).create({
                'name': "Optional-Task3",
                'project_id': project.id,
                'task_number': 3,
                'stage_id': optional_stage_id,
                'optional_task': True,
                'color': 11,
                'instruction': 'Instruction 3',
                'sequence': 11
            })
            task_obj.with_context(from_sale_order=True).create({
                'name': "Optional-Task4",
                'project_id': project.id,
                'task_number': 4,
                'stage_id': optional_stage_id,
                'optional_task': True,
                'color': 11,
                'instruction': 'Instruction 4',
                'sequence': 12
            })
        return super(SaleOrder, self).action_confirm()