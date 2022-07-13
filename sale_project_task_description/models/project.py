from odoo import models, fields, _, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    object_description = fields.Char(string="Objektbeskrivning")

    product_id = fields.Many2one(related='sale_line_id.product_id', store=True)
    
    categ_id = fields.Many2one(related='product_id.categ_id', store=True)
