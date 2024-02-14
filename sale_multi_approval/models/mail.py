# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        """ - mass_mailing: we cannot render, so return the template values
            - normal mode: return rendered values
            /!\ for x2many field, this onchange return command instead of ids
        """
        res = super().onchange_template_id(template_id, composition_mode, model, res_id)

        _logger.error(f"{res.get('value', {}).get('attachment_ids')=} and {model=}")
        if res.get("value", {}).get("attachment_ids") and model == "sale.order":
            _logger.warning(f'{res=}')
            _logger.warning(f'{res["value"]=}')
            _logger.warning(f'{res["value"]["attachment_ids"]=}')
            _logger.warning(f'{res["value"]["attachment_ids"][0]=}')
            _logger.warning(f'{res["value"]["attachment_ids"][0][2]=}')
            new_report = self.env["ir.attachment"].browse(res["value"]["attachment_ids"][0][2][0])
            actual_model = self.env[model].browse(res_id)
            existing_report = self.env["ir.attachment"].search(
                [("res_model", "=", model), ("res_id", "=", res_id), ("name", "=", actual_model.name)])
            if new_report.name == existing_report.name:
                new_report.unlink()
                res["value"]["attachment_ids"][0][2][0] = existing_report.id

        return res

