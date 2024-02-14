# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)
import requests
import werkzeug
from odoo.http import request
import json
import base64
from odoo.exceptions import UserError, ValidationError


class SaleApproval(models.Model):
    _name = 'sale.approval'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sale Order Multi Approval'

    name = fields.Char(default='Approval Configuration')
    approve_customer_sale = fields.Boolean(string="Approval on Sale Orders",
                                           help='Enable this field for adding the approvals for the Sale Orders')
    threshold = fields.Integer("Threshold for double signing", default=200000)

    def apply_configuration(self):
        """Function for applying the approval configuration"""
        return True


class ApprovalLine(models.Model):
    _name = 'approval.line'
    _description = 'Approval line in Sale Order'
    _rec_name = 'approver_id'

    sale_order_id = fields.Many2one('sale.order', readonly=0)
    approver_id = fields.Many2one('res.users', string='Approver', readonly=1)
    approval_status = fields.Boolean(string='Status', readonly=1)
    signed_document = fields.Binary(string='Is Document Signed', readonly=1)
    signed_xml_document = fields.Many2one("ir.attachment", "Signed Document", readonly=1)
    signer_ca = fields.Binary(string='Signer Ca', readonly=1)
    assertion = fields.Binary(string='Assertion', readonly=1)
    relay_state = fields.Binary(string='Relay State', readonly=1)
    signed_on = fields.Datetime(string='Signed on')

    @api.depends('approval_status')
    def _compute_color(self):
        for rec in self:
            if rec.approval_status:
                rec.color = 10
            else:
                rec.color = 1

    color = fields.Integer(string="Color", compute=_compute_color)

    def unlink(self):
        if self.signed_document or self.signed_xml_document or self.approval_status or self.signed_on:
            raise UserError(_("You are not allowed to remove this approval line"))
        return super(ApprovalLine, self).unlink()

