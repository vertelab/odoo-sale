from urllib import request
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class ElkSmsSaleOrder(models.TransientModel):
    _name = "elk.sms"
    _inherit = ['mail.render.mixin']
    _description = "Send SMS to Partners"

    def _default_sms_body(self):
        message = self.env['ir.config_parameter'].get_param('elk_sms_premade_message')
        return message

    @api.depends('partner_id')
    def _compute_partner_phone_number(self):
        for rec in self:
            active_ids = self.env.context.get('active_ids')
            partner_phone = self.env['sale.order'].browse(active_ids).mapped('partner_phone')
            if False in partner_phone:
                raise UserError(_("Some partners don't have phone number"))
            if partner_phone:
                rec.number = ','.join(set(partner_phone))
            else:
                rec.number = False

    def _inverse_partner_phone_number(self):
        pass

    number = fields.Char('Number', compute=_compute_partner_phone_number, inverse=_inverse_partner_phone_number)

    @api.onchange("sms_template_id")
    def sms_template_body(self):
        if self.sms_template_id:
            self.body = self.sms_template_id.body

    sms_template_id = fields.Many2one(
        'sms.template', string='SMS Template',
        domain=[('model', '=', 'sale.order')], ondelete='restrict',
        help='This field contains the template of the SMS that will be sent')

    body = fields.Text(default=_default_sms_body)

    def _load_partner_rec(self):
        context = self.env.context
        active_ids = context.get('active_ids')
        partner_ids = self.env['sale.order'].browse(active_ids).mapped('partner_id')
        return partner_ids.ids

    partner_id = fields.Many2many('res.partner', string="Customer", default=_load_partner_rec)
    mail_message_id = fields.Many2one('mail.message', index=True)
    model = fields.Char(default=lambda self: self.env.context.get('active_model'))

    # and create sms object
    def send_sms(self):
        active_ids = self.env.context.get('active_ids')
        sale_ids = self.env['sale.order'].browse(active_ids)
        if sale_ids.filtered(lambda order: order.state != 'ready_to_deliver'):
            raise UserError(_("You cannot send sms if order is not in ready state"))

        for sale in sale_ids:
            formatted_body = self._render_field('body', sale_ids.ids)[sale.id]
            sms = self.env['sms.sms'].create({
                'number': sale.partner_phone,
                'body': formatted_body,
                'partner_id': sale.partner_id.id,
                'rec_model': 'sale.order',
                'rec_id': sale.id
            })
            sms.send()
        sale_ids.write({'sms_sent': True})

