from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _check_line_unlink(self):
        """
        Check wether a line can be deleted or not.

        Lines cannot be deleted if the order is confirmed; downpayment
        lines who have not yet been invoiced bypass that exception.
        :rtype: recordset sale.order.line
        :returns: set of lines that cannot be deleted
        """
        return self.filtered(lambda line: line.state in ('ready_to_deliver','delivered','done') and (line.invoice_lines or not line.is_downpayment))

    def unlink(self):
        if self._check_line_unlink():
            raise UserError(_('You can not remove an order line once the sales order is Locked, Ready to Deliver or Delivered.\nYou should rather set the quantity to 0.'))
        tasks = self.task_id
        tasks.sale_line_id = False
        tasks.sale_order_id = False
        _logger.warning(f"{tasks}")
        res = super(SaleOrderLine, self).unlink()
        tasks.unlink()
        return res
