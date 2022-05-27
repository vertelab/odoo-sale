from odoo import fields, models, api, _

import logging
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
        msg =  _('A sale order is ready to deliver')
        
        for hr_partner_id in  hr_partner_ids:
                
            self.env['mail.activity'].create({
            'display_name': msg,
            'summary':msg,
            'date_deadline': fields.Datetime.now(),
            'user_id': hr_partner_id,
            'res_id':self.id,
            'res_model_id':self.env.ref('sale.model_sale_order').id,
            # ~ 'activity_type_id':4,
            })
        
    def write(self,values):
        res = super(SaleOrder,self).write(values)
        if values.get('state') and values.get('state') == "ready_to_deliver":
            # ~ self.send_message_ready_to_deliver()
            self.create_ready_to_deliver_activity()
        return res
            
    def action_set_to_delivery(self):
        self.state = 'delivered'

        # archieve timesheets
        # ~ if self.tasks_ids.timesheet_ids:
            # ~ for timesheet in self.tasks_ids.timesheet_ids:
                # ~ timesheet.write({
                    # ~ 'active': False
                # ~ })
        # archieve tasks
        for task in self.tasks_ids:
            task.write({
                'active': False
            })
            
    # ~ def action_draft(self):
        # ~ _logger.warning("action_draft action_draft action_draft action_draft")
        # ~ res = super(SaleOrder, self).action_draft()
        # ~ _logger.warning(f"{self.tasks_ids}")
        # ~ for task in self.tasks_ids:
            # ~ _logger.warning(f"{task=}")
            # ~ task.write({
                # ~ 'active': True
        # ~ })
        
        # ~ return res

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

    def _action_cancel(self):
        inv = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')
        inv.button_cancel()
        self._action_unlink_tasks()
        return self.write({'state': 'cancel'})
    
    def _action_unlink_tasks(self):
        # dissocaite with the tasks
        
        if self.tasks_ids:
            self.tasks_ids.write({
                'sale_line_id': False
            })

        # archieve timesheets
        if self.tasks_ids.timesheet_ids:
            for timesheet in self.tasks_ids.timesheet_ids:
                timesheet.unlink()
        # archieve timesheets
        for task in self.tasks_ids:
            task.unlink()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    ready_to_deliver = fields.Boolean(string="Set Products to Ready to Deliver", default=False, copy=False)

    @api.onchange('product_id')
    def _toggle_ready_to_deliver(self):
        if self.product_id and self.product_id.type != 'service' and not self.project_id:
            self.write({
                'ready_to_deliver': True
            })

