from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    sign_provider_id = fields.Many2one('sign.provider', string="Signature Provider")

    sign_definition_id = fields.Many2one('vrtl.sign.definition', string="Signature Definition")



class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "sign.request.mixin"]

    def create_sign_request(self):
        """Override mixin method"""
        if self.sign_definition_id and not self.sign_request_id:
            values = self.sign_definition_id._prepare_vrtl_sign_request_vals_from_record(self)
            self.sign_request_id = self.env['vrtl.sign.request'].create(values)
            self.env.cr.commit()
        return self.sign_request_id

    def generate(self):
        """Your existing method"""
        return self.initiate_signing()

