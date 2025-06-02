import json
import base64
import httpx
import requests
from datetime import datetime
from odoo import models, fields, api, _



class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["res.bankid", "sale.order"]

    def action_confirm(self):
        if not self._has_user_signed_rec():
            return {
                'type': 'ir.actions.client',
                'tag': 'bankid_sign_modal',
                'target': 'new',
                'context': {
                    'default_record_id': self.id,
                    'default_record_model': self._name,
                    'callback_method': 'action_confirm',
                }
            }
        else:
            return super().action_confirm()



