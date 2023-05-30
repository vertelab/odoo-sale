# ~ # coding: utf-8


from odoo import models, api, _
from odoo import fields as osv_fields
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    def get_project_name(self):
        for record in self:
            project_string = ""
            for project in record.project_ids:
                project_string = project_string + " " + project.name
            record.project_name = project_string
    
    project_name = fields.Char(compute="get_project_name")
    
    
