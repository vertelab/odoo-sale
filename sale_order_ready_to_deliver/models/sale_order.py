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

    # ~ def action_send_delivery_message(self):
        # ~ hr_employee_ids = self.env['hr.employee'].search([('get_notified', '=', True), ('work_email', '!=', False)])
        # ~ hr_partner_ids = hr_employee_ids.mapped('address_home_id')

        # ~ ctx = {
            # ~ 'default_model': 'sale.order',
            # ~ 'default_res_id': self.ids[0],
            # ~ 'default_composition_mode': 'comment',
            # ~ 'force_email': True,
            # ~ 'model_description': self.with_context(lang=self.env.context.get('lang')).type_name,
            # ~ 'default_partner_ids': hr_partner_ids.ids,
            # ~ 'default_subject': 'Ready to Deliver',
            # ~ 'default_body': 'A sale order is ready to deliver',
        # ~ }
        # ~ return {
            # ~ 'type': 'ir.actions.act_window',
            # ~ 'view_mode': 'form',
            # ~ 'res_model': 'mail.compose.message',
            # ~ 'views': [(False, 'form')],
            # ~ 'view_id': False,
            # ~ 'target': 'new',
            # ~ 'context': ctx,
        # ~ }
    
    # ~ def send_message_ready_to_deliver(self):
        # ~ hr_employee_ids = self.env['hr.employee'].search([('get_notified', '=', True), ('work_email', '!=', False)])
        # ~ hr_partner_ids = hr_employee_ids.mapped('address_home_id').ids
        # ~ msg =  _('A sale order is ready to deliver')
        # ~ self.message_post(body=msg, partner_ids=hr_partner_ids)
        
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

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    ready_to_deliver = fields.Boolean(string="Set Products to Ready to Deliver", default=False, copy=False)

    @api.onchange('product_id')
    def _toggle_ready_to_deliver(self):
        if self.product_id and self.product_id.type != 'service' and not self.project_id:
            self.write({
                'ready_to_deliver': True
            })

