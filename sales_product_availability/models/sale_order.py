from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()

                if not is_available:
                    is_available = self._double_check_availability(product_qty, precision)

                if not is_available:
                    message = _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
                              (self.product_uom_qty, self.product_uom.name, self.product_id.name,
                               product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name)
                    # We check if some products are available in other warehouses.
                    if float_compare(product.virtual_available, self.product_id.virtual_available,
                                     precision_digits=precision) == -1:
                        message += _('\nThere are %s %s available across all warehouses.\n\n') % \
                                   (self.product_id.virtual_available, product.uom_id.name)
                        for warehouse in self.env['stock.warehouse'].search([]):
                            quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
                            if quantity > 0:
                                message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
                    warning_mess = {
                        'title': _('Not enough inventory!'),
                        'message': message
                    }
                    return {'warning': warning_mess}
        return {}

    def _double_check_availability(self, product_qty, precision):
        """
            - get default location for the selected warehouse
            - check the quantity level of the location
        """
        wh_default_loc_id = self.order_id.warehouse_id.out_type_id.default_location_src_id
        available_quantity = self.env['stock.quant']._get_available_quantity(self.product_id, wh_default_loc_id)
        if float_compare(available_quantity, product_qty, precision_digits=precision) == -1:
            return False
        else:
            return True
