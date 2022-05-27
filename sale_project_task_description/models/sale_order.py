from odoo import models, fields, _, api

# ~ class ProductTemplate(models.Model):
    # ~ _inherit = 'product.template'
    # ~ work_description = fields.Char(string="Work Description")

# ~ class ProductProduct(models.Model):
    # ~ _inherit = 'product.product'
    # ~ work_description = fields.Char(string="Work Description")
    

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    work_description = fields.Char(string="Work Description")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    work_description = fields.Char(string="Work Description")
    
    # ~ @api.onchange('product_id')
    # ~ def product_id_change_set_work_description(self):
        # ~ for record in self: 
            # ~ if record.product_id.work_description:
                # ~ record.work_description = record.product_id.work_description
    
    def _timesheet_create_task_prepare_values(self, project):
        res = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)
        res.update({
            'description': self.work_description,
            'object_description': self.name,
        })
        return res
