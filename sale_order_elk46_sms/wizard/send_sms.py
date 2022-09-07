from urllib import request
from odoo import api, fields, models
import requests
import logging
import json

_logger = logging.getLogger("dmitri")

class ElkSmsSaleOrder(models.TransientModel):
    _name = "elk.sms"

    def _default_sms_body(self):
        message = self.env['ir.config_parameter'].get_param('elk_sms_premade_message')
        return message

    number = fields.Char('Number')
    body = fields.Text(default=_default_sms_body)
    partner_id = fields.Many2one('res.partner', 'Customer')
    mail_message_id = fields.Many2one('mail.message', index=True)
    elk_api_id = fields.Text()
    status = fields.Char()
    sale_id = fields.Integer()

    #and create sms object
    def send_sms(self):
        sms = self.env['sms.sms'].create({'number': self.number, 'body': self.body, 'partner_id': self.partner_id.id})
        res = sms.send(sms.number, sms.body)

        _logger.warning(res.content)
        obj = json.loads(res.content.decode("utf-8"))

        self.elk_api_id = obj['id']
        self.status = 'Sent'
        self.sale_id = self.env.context.get('active_id')

        temp_sms = self.env['temp.elk.sms'].create({'body': self.body, 'number': self.number, 'elk_api_id': self.elk_api_id, 'status': self.status, 'sale_id': self.sale_id})
        _logger.warning(f"{temp_sms=}")

        #look at api results instead of this since its always 200               
        # if res.content == 200:
        #     if (active_id := self.env.context.get('active_id')):
        #         sale_order = self.env['sale.order'].browse(active_id)
        #         sale_order.message_post(body = self.body )

        return res

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.number = self.partner_id.mobile

    # def create_sms_object(self, body, number, id, status, sale_id):
    #     _logger.warning(f"{body} {number} {id} {status} {sale_id}")
    #     temp_sms = self.env['temp.elk.sms'].create({'body': body, 'number': number, 'elk_api_id': id, 'status': 'Sent', 'sale_id': id})
    #     _logger.warning(f"{temp_sms=}")