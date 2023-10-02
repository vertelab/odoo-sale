import logging
from odoo import fields, models, api, _
from odoo.tools.misc import formatLang, get_lang


_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('ready_to_deliver', 'Ready to Deliver'), ('delivered', 'Delivered')])

    def _prepare_confirmation_values(self):
        not_ready_to_deliver = list(self.order_line.filtered(lambda line: not line.ready_to_deliver))
        if not_ready_to_deliver:
            return {
                'state': 'sale',
                'date_order': fields.Datetime.now()
            }
        else:
            return {
                'state': 'ready_to_deliver',
                'date_order': fields.Datetime.now()
            }

    def create_ready_to_deliver_activity(self):
        hr_employee_ids = self.env['hr.employee'].search([('get_notified', '=', True)])
        hr_partner_ids = hr_employee_ids.mapped('user_id').ids
        msg = _('A sale order is ready to deliver')

        for hr_partner_id in hr_partner_ids:
            self.env['mail.activity'].create({
                'display_name': msg,
                'summary': msg,
                'date_deadline': fields.Datetime.now(),
                'user_id': hr_partner_id,
                'res_id': self.id,
                'res_model_id': self.env.ref('sale.model_sale_order').id,
                # ~ 'activity_type_id':4,
            })

    def write(self, values):
        res = super(SaleOrder, self).write(values)
        if values.get('state') and values.get('state') == "ready_to_deliver":
            # ~ self.send_message_ready_to_deliver()
            self.create_ready_to_deliver_activity()
        return res

    def action_set_to_delivery(self):
        self.state = 'delivered'
        for task in self.tasks_ids:
            task.write({
                'active': False
            })

    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent'])

        achieved_tasks_ids = self.env['project.task'].sudo().search(
            [('active', '=', False), ('sale_line_id.order_id', '=', self.id)]
        )
        if achieved_tasks_ids:
            achieved_tasks_ids.write({'active': True})

        return orders.write({
            'state': 'draft',
            'signature': False,
            'signed_by': False,
            'signed_on': False,
        })

    def _action_unlink_tasks(self):
        # dissociate with the tasks

        if self.tasks_ids:
            self.tasks_ids.write({
                'sale_line_id': False
            })

        # archive timesheet
        if self.tasks_ids.timesheet_ids:
            for timesheet in self.tasks_ids.timesheet_ids:
                timesheet.unlink()
        # archive timesheet
        for task in self.tasks_ids:
            task.unlink()
            
            
    # ~ @api.model
    # ~ def create(self, vals):
        # ~ result = super(SaleOrder, self).create(vals)
        # ~ result.toggle_toggle_ready_to_deliver()
        # ~ return result

    # ~ @api.depends('order_line')
    # ~ def toggle_toggle_ready_to_deliver(self):
        # ~ for record in self:
            # ~ for line in record.order_line:
                # ~ line._toggle_ready_to_deliver()
                
                

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    ready_to_deliver = fields.Boolean(string="Set Products to Ready to Deliver", default=False, copy=False)
    
    @api.model
    def create(self, vals):
        result = super(SaleOrderLine, self).create(vals)
        result._toggle_ready_to_deliver()
        return result

    @api.onchange('product_id')
    def _toggle_ready_to_deliver(self):
        if self.product_id and self.product_id.service_tracking == 'no' and not self.project_id:
            self.write({
                'ready_to_deliver': True
            })
        else:
            self.write({
                'ready_to_deliver': False
            })
            

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        lang = get_lang(self.env, self.order_id.partner_id.lang).code
        product = self.product_id.with_context(
            lang=lang,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        # vals.update(name=self.with_context(lang=lang).get_sale_order_line_multiline_description_sale(product))

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = product._get_tax_included_unit_price(
                self.company_id,
                self.order_id.currency_id,
                self.order_id.date_order,
                'sale',
                fiscal_position=self.order_id.fiscal_position_id,
                product_price_unit=self._get_display_price(product),
                product_currency=self.order_id.currency_id
            )
        else:
            vals['price_unit'] = self.product_id.lst_price
        self.update(vals)

        title = False
        message = False
        result = {}
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s", product.name)
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result
