# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CouponError(Exception):
    pass


class SaleCouponApplyCode(models.TransientModel):
    _inherit = "sale.coupon.apply.code"

    def apply_coupon(self, order, coupon_code):
        error_status = {}
        coupon = self.env['coupon.coupon'].search([('code', '=', coupon_code)], limit=1)
        if coupon and coupon.program_id and coupon.program_id.reward_product_id:
            order._cart_update(
                product_id=coupon.program_id.reward_product_id.id,
                add_qty=coupon.program_id.reward_product_quantity,
            )
        error_status = super(SaleCouponApplyCode, self).apply_coupon(
            order, coupon_code
        )
        if error_status:
            # remove same quantity of products that we added in order to
            # leave the cart in the state that we found it.
            order._cart_update(
                product_id=coupon.program_id.reward_product_id.id,
                add_qty=-coupon.program_id.reward_product_quantity,
            )
        return error_status
