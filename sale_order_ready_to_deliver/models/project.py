from odoo import fields, models, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.onchange('stage_id')
    def update_sale_order_line(self):
        if self.stage_id.ready_to_deliver:
            self.sale_line_id.write({
                'ready_to_deliver': True
            })
        else:
            self.sale_line_id.write({
                'ready_to_deliver': False
            })


class Project(models.Model):
    _inherit = 'project.task.type'

    ready_to_deliver = fields.Boolean(string="Set Products to Ready to Deliver")




