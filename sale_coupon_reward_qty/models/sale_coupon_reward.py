from odoo import models, _

class SaleCouponReward(models.Model):
    _inherit = "sale.order"

    def _get_reward_values_product(self,program):
        price_unit = self.order_line.filtered(lambda line: program.reward_product_id == line.product_id)[0].price_reduce
        taxes = self.fiscal_position_id.map_tax(program.reward_product_id.taxes_id)

        res = {
            'product_id': program.discount_line_product_id.id,
            'price_unit': - price_unit,
            'product_uom_qty': program.reward_product_quantity, # Here we simply return the number of free products set in the coupon
            'is_reward_line': True,
            'name': _("Free Product") + " - " + program.reward_product_id.name,
            'product_uom': program.reward_product_id.uom_id.id,
            'tax_id': [(4, tax.id, False) for tax in taxes],
        }
        return res
