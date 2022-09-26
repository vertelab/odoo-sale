from urllib import request
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class ElkSmsSaleOrder(models.TransientModel):
    _name = "elk.sms"
    _description = "Send SMS to Partners"

    def _default_sms_body(self):
        message = self.env['ir.config_parameter'].get_param('elk_sms_premade_message')
        return message

    @api.depends('partner_id')
    def _compute_partner_phone_number(self):
        for rec in self:
            active_ids = self.env.context.get('active_ids')
            partner_phone = self.env['sale.order'].browse(active_ids).mapped('partner_phone')
            print(partner_phone)
            if False in partner_phone:
                raise UserError(_("Some partners don't have phone number"))
            if partner_phone:
                rec.number = ','.join(set(partner_phone))
            else:
                rec.number = False

    def _inverse_partner_phone_number(self):
        pass

    number = fields.Char('Number', compute=_compute_partner_phone_number, inverse=_inverse_partner_phone_number)
    body = fields.Text(default=_default_sms_body)

    def _load_partner_rec(self):
        context = self.env.context
        active_ids = context.get('active_ids')
        partner_ids = self.env['sale.order'].browse(active_ids).mapped('partner_id')
        return partner_ids.ids

    partner_id = fields.Many2many('res.partner', string="Customer", default=_load_partner_rec)
    mail_message_id = fields.Many2one('mail.message', index=True)
    elk_api_id = fields.Text()
    status = fields.Char()
    sale_id = fields.Integer()
    res_ids = fields.Char('Document IDs')

    # and create sms object
    def send_sms(self):
        active_ids = self.env.context.get('active_ids')
        sale_ids = self.env['sale.order'].browse(active_ids)
        if sale_ids.filtered(lambda order: order.state != 'ready_to_deliver'):
            raise UserError(_("You cannot send sms if order is not in ready state"))

        phone_number = self.number.split(",")
        for partner_id, phone_number in zip(self.partner_id, phone_number):
            sms = self.env['sms.sms'].create({'number': phone_number, 'body': self.body, 'partner_id': partner_id.id})

            res = sms.send(sms.number, sms.body)
            if res.status_code == 200:
                response = json.loads(res.content.decode("utf-8"))
                self.elk_api_id = response.get('id', False)
                self.status = 'Sent'
                self.sale_id = self.env.context.get('active_id')
            else:
                response = res.content.decode("utf-8")
                raise ValidationError(_(response))

            temp_sms = self.env['temp.elk.sms'].create(
                {'body': self.body, 'number': phone_number, 'elk_api_id': self.elk_api_id, 'status': self.status,
                 'sale_id': self.sale_id})
            _logger.warning(f"{temp_sms=}")

        sale_ids.write({'sms_sent': True})
