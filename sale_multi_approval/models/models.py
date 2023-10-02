# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)
import requests
import werkzeug
from odoo.http import request
import json
import base64
from odoo.exceptions import UserError
from datetime import datetime
import uuid
import re
from bs4 import BeautifulSoup
import requests


class AddApproverWizard(models.TransientModel):
    _name = "approver.add.wizard"
    _description = "Approval Wizard"

    def _get_sale_order(self):
        sale_order = self.env["sale.order"].browse(self.env.context.get('active_ids'))
        return sale_order

    @api.model
    def _get_approvers_domain(self):
        group_ids = []
        group_ids.append(self.env.ref('sale_multi_approval.group_approve_manager').id)
        group_ids.append(self.env.ref('sale_multi_approval.group_approver').id)
        # group_ids.append(self.env.ref('res_user_groups_skogsstyrelsen.group_sks_saljare').id)
        offlimit_ids = [i.id for i in self.env["sale.order"].browse(self.env.context.get('active_ids')).approval_ids]
        # offlimit_ids.append(self.env.uid)
        return [('groups_id', 'in', group_ids), ('id', 'not in', offlimit_ids)]

    sale_order = fields.Many2one(comodel_name='sale.order', string='Sale Order', default=_get_sale_order, readonly=True)
    user_id = fields.Many2one(comodel_name='res.users', string='Approver to add', domain=_get_approvers_domain)

    def set_approver(self):
        line = self.env["approval.line"].create(
            {'approver_id': self.user_id.id, 'sale_order_id': self.sale_order.id, 'approval_status': False})
        self.sale_order.write({'approval_ids': [(4, line.id, 0)]})


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
            # ~ if res["value"]["attachment_ids"][0][2]:
            new_report = self.env["ir.attachment"].browse(res["value"]["attachment_ids"][0][2][0])
            actual_model = self.env[model].browse(res_id)
            existing_report = self.env["ir.attachment"].search(
                [("res_model", "=", model), ("res_id", "=", res_id), ("name", "=", actual_model.name)])
            if new_report.name == existing_report.name:
                new_report.unlink()
                res["value"]["attachment_ids"][0][2][0] = existing_report.id

        return res


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

    sale_order_id = fields.Many2one('sale.order', readonly=0)
    approver_id = fields.Many2one('res.users', string='Approver', readonly=1)
    approval_status = fields.Boolean(string='Status', readonly=1)
    signed_document = fields.Binary(string='Is Document Signed', readonly=1)
    signed_xml_document = fields.Many2one("ir.attachment", "Signed Document", readonly=1)
    signer_ca = fields.Binary(string='Signer Ca', readonly=1)
    assertion = fields.Binary(string='Assertion', readonly=1)
    relay_state = fields.Binary(string='Relay State', readonly=1)
    signed_on = fields.Datetime(string='Signed on')

    def unlink(self):
        if self.signed_document or self.signed_xml_document or self.approval_status or self.signed_on:
            raise UserError(_("You are not allowed to remove this approval line"))
        return super(ApprovalLine, self).unlink()


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_ids = fields.One2many('approval.line', 'sale_order_id')
    document_fully_approved = fields.Boolean(compute='_compute_document_fully_approved')
    check_approve_ability = fields.Boolean(compute='_compute_check_approve_ability')
    is_approved = fields.Boolean(compute='_compute_is_approved')
    page_visibility = fields.Boolean(compute='_compute_page_visibility')
    quotation_locked = fields.Boolean()
    signed_document = fields.Binary(string='Is Document Signed', readonly=1, copy=False)
    signed_xml_document = fields.Many2one("ir.attachment", "Signed XML Document", readonly=1, copy=False)
    signer_ca = fields.Binary(string='Signer Ca', readonly=1, copy=False)
    assertion = fields.Binary(string='Assertion', readonly=1, copy=False)
    relay_state = fields.Binary(string='Relay State', readonly=1, copy=False)

    @api.depends('partner_id')
    def _compute_user_group(self):
        for rec in self:
            logged_in_user = self.env.user
            # ~ if logged_in_user.has_group('res_user_groups_skogsstyrelsen.group_sks_saljare'):
            if logged_in_user.has_group('sale_multi_approval.group_approver') or logged_in_user.has_group(
                    'sale_multi_approval.group_approve_manager'):
                rec.has_sign_group = True
            else:
                rec.has_sign_group = False

    has_sign_group = fields.Boolean(string="Has Sign Group", compute=_compute_user_group)

    @api.model_create_multi
    def create(self, vals):
        records = super().create(vals)
        for record in records:
            if record.require_signature:
                approval_vals = {
                    'approver_id': record.user_id.id,
                    'sale_order_id': record.id
                }
                line = self.env["approval.line"].sudo().create(approval_vals)
                record.write({'approval_ids': [(4, line.id, 0)]})
        return records

    @api.depends('approval_ids')
    def _compute_page_visibility(self):
        """Compute function for making the approval page visible/invisible"""
        if self.approval_ids:
            self.page_visibility = True
        else:
            self.page_visibility = False

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
        self.signed_xml_document = False
        self.signer_ca = False
        self.assertion = False
        self.relay_state = False
        self.signed_by = False
        self.signed_on = False
        self.state = "draft"
        for signature in self.approval_ids:
            signature.write(
                {'approval_status': False, 'signed_xml_document': None, 'signer_ca': None, 'assertion': None,
                 'relay_state': None, 'signed_on': False})
        _logger.warning(f"{self.name=}")
        _logger.warning(
            f"{self.env['ir.attachment'].search([('name', '=', f'Offert {self.name}'), ('res_model', '=', 'sale.order'), ('res_id', '=', self.id)])=}")

        self.env["ir.attachment"].search(
            [('name', '=', f'Offert {self.name}'), ('res_model', '=', 'sale.order'), ('res_id', '=', self.id)]).unlink()

    def sale_approve(self, **kwargs):
        if not self and kwargs:
            self = self.env['sale.order'].browse(int(kwargs.get('order_id')))
        """This is the function of the approve button also
        updates the approval table values according to the
        approval of the users"""

        current_user = self.env.uid

        for approval_id in self.approval_ids:
            _logger.warning(f"{approval_id=}, {current_user=}")

            if current_user == approval_id.approver_id.id:
                signport = self.env.ref("rest_signport.api_signport")
                data = json.loads(request.httprequest.data)
                access_token = data.get("params", {}).get("access_token")
                res = signport.sudo().post_sign_sale_order(
                    ssn=self.env.user.partner_id.social_sec_nr and self.env.user.partner_id.social_sec_nr.replace("-",
                                                                                                                  "") or False,
                    order_id=self.id,
                    access_token=access_token,
                    message="Signering av offert",
                    sign_type="employee",
                    approval_id=approval_id.id,
                )
                # _logger.warning(f"sale_approve res: {res}")
                base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

                if res.get('signingServiceUrl'):
                    signport_request = self.env["signport.request"].sudo().create({
                        'relay_state': res['relayState'],
                        'eid_sign_request': res['eidSignRequest'],
                        'binding': res['binding'],
                        'signing_service_url': res['signingServiceUrl']
                    })
                    _logger.warning(f"returning the view, signport request: {signport_request}")
                    print(f"{base_url}/web/signport_form/{self.id}/{signport_request.id}/start_sign")
                return {
                    'type': 'ir.actions.act_url',
                    'target': 'self',
                    'url': f"{base_url}/web/signport_form/{self.id}/{signport_request.id}/start_sign",
                    #'url': f"{base_url}/web#id={self.id}&model=sale.order&view_type=form"

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
        if length_approve_lines >= 1 and self.amount_total < self.env.ref(
                "sale_multi_approval.default_sale_multi_approval_config").threshold:
            self.document_fully_approved = True
        elif length_approve_lines >= 2:
            self.document_fully_approved = True
        else:
            self.document_fully_approved = False

    latest_pdf_export = fields.Many2one("ir.attachment", string="Latest PDF Export", copy=False)

    def access_token_sale_order(self, **kwargs):
        if not self and kwargs:
            self = self.env['sale.order'].browse(int(kwargs.get('order_id')))
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': f"{web_base_url}{self.get_portal_url()}",
        }

    def action_sign_order(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': f"/trigger/signature/{self.id}",
        }


class Attachment(models.Model):
    _inherit = "ir.attachment"

    def create_attachment(self, **kwargs):
        attachment_id = self.env['ir.attachment'].sudo().create(kwargs)
        sale_id = self.env[attachment_id.res_model].sudo().browse(attachment_id.res_id)
        sale_id.write({'latest_pdf_export': attachment_id.id})


class RestApiSignport(models.Model):
    _inherit = "rest.api"

    # def get_keys(self, dl, keys_list):
    #     if isinstance(dl, dict):
    #         keys_list += dl.keys()
    #         map(lambda x: get_keys(x, keys_list), dl.values())
    #     elif isinstance(dl, list):
    #         map(lambda x: get_keys(x, keys_list), dl)

    def post_sign_sale_order(self, ssn, order_id, access_token, message=False, sign_type="customer", approval_id=False):
        # export_wizard = self.env['xml.export'].with_context({'active_model': 'sale.order', 'active_ids': order_id}).create({})
        # action = export_wizard.download_xml_export()
        # self.env['ir.attachment'].browse(action['res_id']).update({'res_id': order_id, 'res_model': 'sale.order'})

        # document = (
        #     self.env["ir.attachment"]
        #     .sudo()
        #     .search(
        #         [
        #             ("res_model", "=", "sale.order"),
        #             ("res_id", "=", order_id),
        #             ("mimetype", "=", "application/pdf"),
        #         ],
        #         limit=1,
        #     )
        # )
        # if not document:
        #     return False
        # # TODO: attach pdf or xml of order to the request

        # document = self.env['sale.order'].browse(order_id).latest_xml_export
        document = self.env['sale.order'].browse(order_id).latest_pdf_export
        if self.env['sale.order'].browse(order_id).signed_xml_document:
            document_content = self.env['sale.order'].browse(order_id).signed_xml_document.datas.decode()
        else:
            document_content = document.datas.decode()

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json; charset=utf8",
        }

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        _logger.warning(f"sign_type sign_type sign_type: {sign_type}")

        role = self.employee_string
        session_id = request.httprequest.cookies.get('session_id')
        _logger.info(f"session_id: {session_id}")
        response_url = f"{base_url}/web/{order_id}/{approval_id}/sign_complete?session_id={session_id}"

        if sign_type == "customer":
            role = self.customer_string
            response_url = f"{base_url}/my/orders/{order_id}/sign_complete?access_token={access_token}"

        guid = str(uuid.uuid1())

        add_signature_page_vals = {
            "clientCorrelationId": guid,
            "documents": [
                {
                    "content": document_content,
                    "signaturePageTemplateId": "e33d2a21-1d23-4b4f-9baa-def11634ceb4",
                    "signaturePagePosition": "last",
                }
            ]
        }

        res = self.call_endpoint(
            method="POST",
            endpoint_url="/AddSignaturePage",
            headers=headers,
            data_vals=add_signature_page_vals,
        )
        document_content = res['documents'][0]['content']
        #document_content = json.loads(res.get('data'))['documents'][0]['content']

        displayname = False
        if self.env.user.firstname:
            displayname = self.env.user.firstname
        if self.env.user.lastname:
            if displayname:
                displayname = f"{displayname} {self.env.user.lastname}"
            else:
                displayname = self.env.user.lastname

        get_sign_request_vals = {
            "username": f"{self.user}",
            "password": f"{self.password}",
            "spEntityId": f"{self.sp_entity_id}",  # "https://serviceprovider.com/", # lägg som inställning på rest api
            "idpEntityId": f"{self.idp_entity_id}",
            "signResponseUrl": response_url,
            "signatureAlgorithm": f"{self.signature_algorithm}",
            "loa": f"{self.loa}",
            "certificateType": "PKC",
            "signingMessage": {
                "body": f"{message}",
                "mustShow": True,
                "encrypt": True,
                "mimeType": "text",
            },
            "document": [
                {
                    "mimeType": 'application/pdf',  # document.mimetype,  # TODO: check mime type
                    "content": document_content,  # TODO: include document to sign
                    "fileName": document.display_name + 'Signed',  # TODO: add filename
                    # "encoding": False  # TODO: should we use this?
                    "documentName": document.display_name + 'Signed',  # TODO: what is this used for?
                    "adesType": "bes",  # TODO: what is "ades"? "bes" or "none"
                }
            ],
            "requestedSignerAttribute": [
                {
                    "name": "urn:oid:1.2.752.29.4.13",  # swedish "personnummer", hardcoded
                    "type": "xsd:string",
                    "value": f"{ssn}",
                }
            ],
            "signaturePage": {
                "initialPosition": "last",
                "templateId": "e33d2a21-1d23-4b4f-9baa-def11634ceb4",
                "allowRemovalOfExistingSignatures": False,
                "signerAttributes": [
                    {
                        "label": _("Role"),
                        "value": role
                    },
                    {
                        "label": "Kontonamn",
                        "value": displayname,
                    },
                ],
                "signatureTitle": "Signerad av",
            },
        }
        res = self.call_endpoint(
            method="POST",
            endpoint_url="/GetSignRequest",
            headers=headers,
            data_vals=get_sign_request_vals,
        )

        return res

    def signport_post(self, data_vals=None, order_id=False, endpoint=False, sign_type="customer"):
        if data_vals is None:
            data_vals = {}

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json; charset=utf8",
        }
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        data_vals["username"] = f"{self.user}"
        data_vals["password"] = f"{self.password}"
        res = self.call_endpoint(
            method="POST",
            endpoint_url=endpoint,
            headers=headers,
            data_vals=data_vals,
        )

        if not res['status']['success']:
            if 'not valid personal number' in res['status']['statusCodeDescription']:
                raise UserError(_('Invalid Personal number, please format it like "YYYYMMDDXXXX"'))
            elif 'SignatureResponseUserCancel' in res['status']['statusCode']:
                raise UserError(_('Digital signing cancelled'))
            elif 'The request was canceled' in res['status']['statusCodeDescription']:
                raise UserError('Digital signing cancelled')
            elif ('The signer attributes in the sign request cannot be verified against the attributes of the '
                  'authenticated user') in \
                    res['status']['statusCodeDescription']:
                raise UserError('Mismatching personal numbers')

            else:
                match = re.search("StatusMessage: \'(.)+\'", res['status']['statusCodeDescription'])
                if not match:
                    match = re.search("Message.*\'(.)+\'", res['status']['statusCodeDescription'])
                if match:
                    raise UserError(match[0])
                else:
                    raise UserError(res['status']['statusCodeDescription'])

        attachment = self.env['ir.attachment'].create(
            {
                'mimetype': 'application/pdf',
                'datas': res["document"][0]["content"],
                'name': res["document"][0]['fileName'],
                'res_model': 'sale.order',
                'res_id': order_id
            }
        )

        if sign_type == "employee":
            _logger.warning(f"employee self.env.uid: {self.env.user}")
            self.env['sale.order'].browse(order_id).signed_xml_document = attachment

            approval_line = self.env["approval.line"].search(
                [("sale_order_id", "=", order_id), ("approver_id", "=", self.env.uid)], limit=1)
            approval_line.approval_status = True
            approval_line.signed_xml_document = attachment
            approval_line.signer_ca = res["signerCa"]
            approval_line.assertion = res["assertion"]
            approval_line.relay_state = base64.b64encode(res["relayState"].encode())
            approval_line.signed_on = fields.Datetime.now()

        elif sign_type == "customer":
            sale_order = self.env["sale.order"].sudo().browse(order_id)

            sale_order.signed_xml_document = attachment
            sale_order.signer_ca = res["signerCa"]
            sale_order.assertion = res["assertion"]
            sale_order.relay_state = base64.b64encode(res["relayState"].encode())
            sale_order.write(
                {
                    "signed_by": self.env.user.name,
                    "signed_on": datetime.now(),
                }
            )
            sale_order.action_confirm()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    quotation_locked = fields.Boolean(string="Lock Quotation", related="order_id.quotation_locked")
