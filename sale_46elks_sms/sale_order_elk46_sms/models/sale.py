from odoo import models, fields, api, _


class Sale(models.Model):
    _inherit = 'sale.order'

    sms_sent = fields.Boolean(string="SMS Sent", readonly=True)
