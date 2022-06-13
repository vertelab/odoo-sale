from odoo import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    estimated_time = fields.Float(string="Estimated Time", copy=False, related='product_id.estimated_time', readonly=False, store=True)


    def _convert_qty_company_hours(self, dest_company):
        company_time_uom_id = dest_company.project_time_mode_id
        if self.product_uom.id != company_time_uom_id.id and self.product_uom.category_id.id == company_time_uom_id.category_id.id:
            planned_hours = self.product_uom._compute_quantity(self.product_uom_qty, company_time_uom_id) * self.estimated_time
        else:
            planned_hours = self.product_uom_qty * self.estimated_time
        return planned_hours

    