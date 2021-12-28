from odoo import fields, models, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.onchange('stage_id')
    def update_sale_order_line(self):
        if self.stage_id.ready_to_deliver:
            self.sale_line_id.write({
                'ready_to_deliver': True
            })
            not_ready_to_deliver = list(self.sale_order_id.order_line.filtered(lambda line: not line.ready_to_deliver))
            if not not_ready_to_deliver and self.sale_order_id.state in ['sale', 'done']:
                self.sale_order_id.write({
                    'state': 'ready_to_deliver',
                })
        else:
            self.sale_line_id.write({
                'ready_to_deliver': False
            })
            if self.sale_order_id.state == "ready_to_deliver" or self.sale_order_id.state == "delivered":
                self.sale_order_id.write({
                        'state': 'sale',
                })


class Project(models.Model):
    _inherit = 'project.task.type'

    ready_to_deliver = fields.Boolean(string="Set Products to Ready to Deliver")




