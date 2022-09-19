from urllib import request
from odoo import api, fields, models
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class SaveElkSms(models.Model):
    _name = 'temp.elk.sms'
    _description = "Saved ELK SMS"

    number = fields.Char()
    body = fields.Text()
    elk_api_id = fields.Text()
    status = fields.Char()
    sale_id = fields.Integer()
