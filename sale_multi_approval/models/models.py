# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests
import werkzeug
from odoo.http import request
import json
import base64
    
class AddApproverWizard(models.TransientModel):
    _name="approver.add.wizard"
    def _get_sale_order(self):
        sale_order = self.env["sale.order"].browse(self.env.context.get('active_ids'))
        return sale_order
    @api.model
    def _get_approvers_domain(self):
        group_ids = []
        group_ids.append(self.env.ref('sale_multi_approval.group_approve_manager').id)
        group_ids.append(self.env.ref('sale_multi_approval.group_approver').id)
        group_ids.append(self.env.ref('res_user_groups_skogsstyrelsen.group_sks_saljare').id)
        offlimit_ids = [i.id for i in self.env["sale.order"].browse(self.env.context.get('active_ids')).approval_ids]
        # offlimit_ids.append(self.env.uid)
        _logger.warning("#"*99)
        _logger.warning(self.env["sale.order"].browse(self.env.context.get('active_ids')).approval_ids)
        return [('groups_id', 'in', group_ids), ('id', 'not in', offlimit_ids)]

    sale_order = fields.Many2one(comodel_name='sale.order', string='Sale Order', default=_get_sale_order, readonly=True)
    user_id = fields.Many2one(comodel_name='res.users', string='Approver to add', domain= _get_approvers_domain)

    def set_approver(self):
        line = self.env["approval.line"].create({'approver_id': self.user_id.id, 'sale_order_id': self.sale_order.id, 'approval_status': False})
        self.sale_order.write({'approval_ids': [(4, line.id, 0)]})
    
    
    

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        """ - mass_mailing: we cannot render, so return the template values
            - normal mode: return rendered values
            /!\ for x2many field, this onchange return command instead of ids
        """
        res = super().onchange_template_id(template_id, composition_mode, model, res_id)
        if res.get("value",{}).get("attachment_ids") and model == "sale.order":
            new_report = self.env["ir.attachment"].browse(res["value"]["attachment_ids"][0][2][0])
            existing_report = self.env["ir.attachment"].search([("res_model", "=", model), ("res_id", "=", res_id)])
            if new_report.name == existing_report.name:
                new_report.unlink()
                res["value"]["attachment_ids"][0][2][0] = existing_report.id


        return res

class SignportRequest(models.TransientModel):
    _name = 'signport.request'

    relay_state = fields.Char()
    eid_sign_request = fields.Char()
    binding = fields.Char()
    signing_service_url = fields.Char()
    
    

    def apply_configuration(self):
        """Function for applying the approval configuration"""
        return True

class SaleApproval(models.Model):
    _name = 'sale.approval'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sale Order Multi Approval'

    name = fields.Char(default='Approval Configuration')
    approve_customer_sale = fields.Boolean(string="Approval on Sale Orders",
                                              help='Enable this field for adding the approvals for the Sale Orders')
    sale_approver_ids = fields.Many2many('res.users', 'sale_id', string='Sale Approver', domain=lambda self: [
        ('groups_id', 'in', self.env.ref('base.group_user').id)],
                                            help='In this field you can add the approvers for the Sale Order')
    
    

    def apply_configuration(self):
        """Function for applying the approval configuration"""
        return True


class ApprovalLine(models.Model):
    _name = 'approval.line'
    _description = 'Approval line in Sale Order'

    sale_order_id = fields.Many2one('sale.order', readonly=0)
    approver_id = fields.Many2one('res.users', string='Approver', readonly=1)
    approval_status = fields.Boolean(string='Status', readonly=1)
    signed_document = fields.Binary(string='Signed Document', readonly=1)
    signer_ca = fields.Binary(string='Signer Ca', readonly=1)
    assertion = fields.Binary(string='Assertion', readonly=1)
    relay_state = fields.Binary(string='Relay State', readonly=1)
    
    

class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_ids = fields.One2many('approval.line', 'sale_order_id')
    document_fully_approved = fields.Boolean(compute='_compute_document_fully_approved')
    check_approve_ability = fields.Boolean(compute='_compute_check_approve_ability')
    is_approved = fields.Boolean(compute='_compute_is_approved')
    page_visibility = fields.Boolean(compute='_compute_page_visibility')
    quotation_locked = fields.Boolean()
    signed_document = fields.Binary(string='Signed Document', readonly=1)
    signer_ca = fields.Binary(string='Signer Ca', readonly=1)
    assertion = fields.Binary(string='Assertion', readonly=1)
    relay_state = fields.Binary(string='Relay State', readonly=1)


    @api.model_create_multi
    def create(self, vals):
        records = super(SaleOrder, self).create(vals)
        _logger.warning("here"*99)
        _logger.warning(records)
        for record in records:
            _logger.warning(f"record: {record}")
            approval_vals = {
            'approver_id': record.user_id.id,
            'sale_order_id': record.id
             }
            line = self.env["approval.line"].sudo().create(approval_vals)
            _logger.warning(line.read())
            record.write({'approval_ids': [(4, line.id, 0)]})
            _logger.warning(f"approver_ids: {record.approval_ids}")
        return records

    def generate_sale_pdf(self):
        report_name = self.name
        report = self.env.ref("sale.action_report_saleorder")
        report_service = report.report_name

        if report.report_type in ['qweb-html', 'qweb-pdf']:
            result, format = report._render_qweb_pdf([self.id])
        else:
            res = report._render([self.id])
            result, format = res

        # TODO in trunk, change return format to binary to match message_post expected format
        result = base64.b64encode(result)
        ext = "." + format
        if not report_name.endswith(ext):
            report_name += ext
        attachment = (report_name, result)
        data_attach = {
            'name': attachment[0],
            'datas': attachment[1],
            'res_model': 'sale.order',
            'res_id': self.id,
            'type': 'binary',  # override default_type from context, possibly meant for another model!
        }
        self.env["ir.attachment"].create(data_attach)


    

    @api.depends('approval_ids')
    def _compute_page_visibility(self):
        """Compute function for making the approval page visible/invisible"""
        if self.approval_ids:
            self.page_visibility = True
        else:
            self.page_visibility = False

    # @api.onchange('partner_id')
    # def _onchange_partner_id(self):
    #     """This is the onchange function of the partner which loads the
    #     persons for the approval to the approver table of the account.move"""
    #     # sale_approval_id = self.env['sale.approval'].search([])
    #     # self.approval_ids = None
    #     # if sale_approval_id.approve_customer_sale:
    #     _logger.warning(f"SET APROVER IDS"*99)
    #     vals = {
    #         'approver_id': self.user_id.id,
    #         'sale_order_id': self.id
    #     }
    #     line = self.env["approval.line"].sudo().create(vals)
    #     self.write({'approval_ids': [(4, line, 0)]})
    #     _logger.warning(f"line: {line}")

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

    def sale_unlock(self):
        self.quotation_locked = False
        for signature in self.approval_ids:
            signature.write({'approval_status': False, 'signed_document': None, 'signer_ca': None, 'assertion': None, 'relay_state': None})
        self.env["ir.attachment"].search([('name', '=', f'{self.name}.pdf'), ('res_model', '=', 'sale.order'), ('res_id', '=', self.id)], limit=1).unlink()

    def sale_approve(self):
        """This is the function of the approve button also
        updates the approval table values according to the
        approval of the users"""
        self.ensure_one()
        current_user = self.env.uid
        if not self.env["ir.attachment"].search([
            ("res_model", "=", "sale.order"),
            ("res_id", "=", self.id),
            ("name", "=", f"{self.name}.pdf"),
            ]):
            self.generate_sale_pdf()
        for approval_id in self.approval_ids:
            if current_user == approval_id.approver_id.id:
                signport = self.env.ref("rest_signport.api_signport")
                data = json.loads(request.httprequest.data)
                access_token=data.get("params", {}).get("access_token")
                res = signport.sudo().post_sign_sale_order(
                    ssn=self.env.user.partner_id.social_sec_nr and self.env.user.partner_id.social_sec_nr.replace("-", "") or False,
                    order_id=self.id,
                    access_token=access_token,
                    message="Signering av dokument",
                    sign_type="employee",
                    approval_id=approval_id.id
                )
                _logger.warning(res)
                base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
                signport_request = self.env["signport.request"].sudo().create({
                    'relay_state': res['relayState'],
                    'eid_sign_request': res['eidSignRequest'],
                    'binding': res['binding'],
                    'signing_service_url': res['signingServiceUrl']
                })
                return {
                    'type': 'ir.actions.act_url',
                    'target': 'self',
                    'url': f"{base_url}/web/signport_form/{self.id}/{signport_request.id}/start_sign",
                }

    def _compute_is_approved(self):
        """In this compute function we are verifying whether the document
        is approved/not approved by the current logged in user"""
        current_user = self.env.uid
        if self.order_line and self.approval_ids:
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
        approval_ids = self.approval_ids
        approve_lines = approval_ids.filtered(lambda item: item.approval_status)
        length_approve_lines = len(approve_lines)
        if length_approve_lines >= 1:
            self.quotation_locked = True
        else:
            self.quotation_locked = False
        if  length_approve_lines >= 1 and self.amount_total < 200000:
            self.document_fully_approved = True
        elif length_approve_lines >= 2:
            self.document_fully_approved = True
        else:
            self.document_fully_approved = False
