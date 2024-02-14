# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class AddApproverWizard(models.TransientModel):
    _name = "approver.add.wizard"
    _description = "Approval Wizard"

    def _get_sale_order(self):
        sale_order = self.env["sale.order"].browse(self.env.context.get('active_ids'))
        return sale_order

    sale_order = fields.Many2one(comodel_name='sale.order', string='Sale Order', default=_get_sale_order, readonly=True)

    @api.model
    def _get_approvers_domain(self):
        group_ids = []
        group_ids.append(self.env.ref('sale_multi_approval.group_approve_manager').id)
        group_ids.append(self.env.ref('sale_multi_approval.group_approver').id)
        offlimit_ids = [i.id for i in self.env["sale.order"].browse(self.env.context.get('active_ids')).approval_ids]
        return [('groups_id', 'in', group_ids), ('id', 'not in', offlimit_ids)]

    user_id = fields.Many2one(comodel_name='res.users', string='Approver to add', domain=_get_approvers_domain)

    def set_approver(self):
        line = self.env["approval.line"].create(
            {'approver_id': self.user_id.id, 'sale_order_id': self.sale_order.id, 'approval_status': False})
        self.sale_order.write({'approval_ids': [(4, line.id, 0)]})


class SignportRequest(models.TransientModel):
    _name = 'signport.request'
    _description = 'SingPort Request'

    relay_state = fields.Char()
    eid_sign_request = fields.Char()
    binding = fields.Char()
    signing_service_url = fields.Char()

    def apply_configuration(self):
        """Function for applying the approval configuration"""
        return True



