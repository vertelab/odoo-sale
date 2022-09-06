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

    def send_sms(self):
        sms = self.env['sms.sms'].create({'number': self.number, 'body': self.body, 'partner_id': self.partner_id.id})
        res = sms.send(sms.number, sms.body)

        obj = json.loads(res.content.decode("utf-8"))

        _logger.warning(obj)
        
        #look at api results instead of this since its always 200               
        if res.content == 200:
            if (active_id := self.env.context.get('active_id')):
                sale_order = self.env['sale.order'].browse(active_id)
                sale_order.message_post(body = self.body )

        return res

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.number = self.partner_id.mobile
