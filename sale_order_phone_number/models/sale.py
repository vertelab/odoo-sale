from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_phone = fields.Char(string="Phone", related='partner_id.phone', readonly=False)

    def write(self, values):
        res = super(SaleOrder, self).write(values)
        if self.partner_phone:
            self.partner_id.write({
                'phone': self.partner_phone
            })
        return res
