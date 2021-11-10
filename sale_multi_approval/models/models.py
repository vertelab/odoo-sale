# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleApproval(models.Model):
    _name = 'sale.approval'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sale Order Multi Approval'

    name = fields.Char(default='Approval Configuration')
    approve_customer_invoice = fields.Boolean(string="Approval on Customer Invoice",
                                              help='Enable this field for adding the approvals for the customer invoice')
    sale_approver_ids = fields.Many2many('res.users', 'invoice_id', string='Invoice Approver', domain=lambda self: [
        ('groups_id', 'in', self.env.ref('invoice_multi_approval.group_approver').id)],
                                            help='In this field you can add the approvers for the customer invoice')

    def apply_configuration(self):
        """Function for applying the approval configuration"""
        return True


class ApprovalLine(models.Model):
    _name = 'approval.line'
    _description = 'Approval line in Sale Order'

    sale_order_id = fields.Many2one('sale.order')
    approver_id = fields.Many2one('res.users', string='Approver')
    approval_status = fields.Boolean(string='Status')

class SaleOrder(models.Model):
    _inherit = "sale.order"


    approval_ids = fields.One2many('approval.line', 'move_id')
    document_fully_approved = fields.Boolean(compute='_compute_document_fully_approved')
    check_approve_ability = fields.Boolean(compute='_compute_check_approve_ability')
    is_approved = fields.Boolean(compute='_compute_is_approved')
    page_visibility = fields.Boolean(compute='_compute_page_visibility')

    @api.depends('approval_ids')
    def _compute_page_visibility(self):
        """Compute function for making the approval page visible/invisible"""
        if self.approval_ids:
            self.page_visibility = True
        else:
            self.page_visibility = False

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """This is the onchange function of the partner which loads the
        persons for the approval to the approver table of the account.move"""
        sale_approval_id = self.env['sale.approval'].search([])
        self.approval_ids = None
        if sale_approval_id.approve_customer_invoice:
            for user in sale_approval_id.invoice_approver_ids:
                vals = {
                    'approver_id': user.id
                }
                self.approval_ids |= self.approval_ids.new(vals)

    @api.depends('approval_ids.approver_id')
    def _compute_check_approve_ability(self):
        """This is the compute function which check the current
        logged in user is eligible or not for approving the document"""
        current_user = self.env.uid
        approvers_list = []
        for approver in self.approval_ids:
            approvers_list.append(approver.approver_id.id)
        if current_user in approvers_list:
            self.check_approve_ability = True
        else:
            self.check_approve_ability = False

    def sale_approve(self):
        """This is the function of the approve button also
        updates the approval table values according to the
        approval of the users"""
        self.ensure_one()
        current_user = self.env.uid
        for approval_id in self.approval_ids:
            if current_user == approval_id.approver_id.id:
                approval_id.update({'approval_status': True})

    def _compute_is_approved(self):
        """In this compute function we are verifying whether the document
        is approved/not approved by the current logged in user"""
        current_user = self.env.uid
        if self.invoice_line_ids and self.approval_ids:
            for approval_id in self.approval_ids:
                if current_user == approval_id.approver_id.id:
                    if approval_id.approval_status:
                        self.is_approved = True
                        break
                    else:
                        self.is_approved = False
                else:
                    self.is_approved = False
        else:
            self.is_approved = False

    @api.depends('approval_ids')
    def _compute_document_fully_approved(self):
        """This is the compute function which verifies whether
        the document is completely approved or not"""
        length_approval_ids = len(self.approval_ids)
        approval_ids = self.approval_ids
        approve_lines = approval_ids.filtered(lambda item: item.approval_status)
        length_approve_lines = len(approve_lines)
        if length_approval_ids == length_approve_lines:
            self.document_fully_approved = True
        else:
            self.document_fully_approved = False
