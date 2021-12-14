from odoo import models, fields, _, api


class ProjectTask(models.Model):
    _inherit = 'project.task'
    object_description = fields.Char(string="Objektbeskrivning")
