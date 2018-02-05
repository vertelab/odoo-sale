# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2018 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)


class crm_case_section(models.Model):
    _inherit = "crm.case.section"

    confirm_mail_template = fields.Many2one(comodel_name='email.template',string="Confirm mail")


class sale_order(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def action_button_confirm(self):
        _logger.error('action_button_confirm %s ' % self.env.context)
        template = self.section_id.confirm_mail_template if self.section_id.confirm_mail_template else self.env.ref('sale.email_template_edi_sale')
        super(sale_order,self.with_context(default_template_id=template.id,send_email=True)).action_button_confirm()

    @api.multi
    def force_quotation_send(self):
        _logger.error('force_quotation_send %s ' % self.env.context)
        super(sale_order,self).force_quotation_send()
        return True

    @api.multi
    def action_quotation_send(self):
        res = super(sale_order,self).action_quotation_send()
        res['context']['default_template_id'] = self.env.context.get('default_template_id',res['context'].get('default_template_id'))
        return res
