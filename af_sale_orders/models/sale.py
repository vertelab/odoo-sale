from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        carreer_product_id = self.env.ref('af_sale_orders.kvd_01').id
        interpretor_product_ids = [self.env.ref('af_sale_orders.kvd_tlk_01').id,
                      self.env.ref('af_sale_orders.kvd_tlk_02').id]
        is_interpretor = False
        is_carreer = False
        for line in self.order_line:
            if line.product_id and line.product_id.id == carreer_product_id:
                is_carreer = True
            elif line.product_id and line.product_id.id in interpretor_product_ids:
                is_interpretor = True
        if is_carreer:
            project = self.env['project.project'].create({
                'name': self.partner_id.name
            })
            if is_interpretor:
                task_obj = self.env['project.task']
                task_obj.create({
                    'name': "Task1",
                    'project_id': project.id
                })
                task_obj.create({
                    'name': "Task2",
                    'project_id': project.id
                })
                task_obj.create({
                    'name': "Task3",
                    'project_id': project.id
                })
                
        return super(SaleOrder, self).action_confirm()