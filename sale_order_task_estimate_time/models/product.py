from odoo import fields, models, api, _

import logging

_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = 'product.template'

    estimated_time = fields.Float(string='Estimated Time', compute='_compute_estimated_time',
                                  inverse='_set_estimated_time')

    @api.depends_context('company')
    @api.depends('product_variant_ids', 'product_variant_ids.estimated_time')
    def _compute_estimated_time(self):
        unique_variants = self.filtered(lambda product_template: len(product_template.product_variant_ids) == 1)
        for template in unique_variants:
            template.estimated_time = template.product_variant_ids.estimated_time
        for template in (self - unique_variants):
            template.estimated_time = 0.0

    def _set_estimated_time(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.estimated_time = template.estimated_time


class ProductProduct(models.Model):
    _inherit = 'product.product'

    estimated_time = fields.Float(string='Estimated Time')


