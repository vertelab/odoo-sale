# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class Attachment(models.Model):
    _inherit = "ir.attachment"

    def create_attachment(self, **kwargs):
        attachment_id = self.env['ir.attachment'].sudo().create(kwargs)
        sale_id = self.env[attachment_id.res_model].sudo().browse(attachment_id.res_id)
        sale_id.write({'latest_pdf_export': attachment_id.id})


