from odoo import models, fields, api, _

import logging

from odoo.http import request
import json
import base64
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_line = fields.One2many(
        'sale.order.line',
        'order_id',
        string='Order Lines',
        states={'cancel': [('readonly', True)], 'done': [('readonly', False)]}, copy=True, auto_join=True)

    approval_ids = fields.One2many('approval.line', 'sale_order_id')

    @api.depends('approval_ids')
    def _compute_approval_ids(self):
        for rec in self:
            if rec.approval_ids:
                rec.many_approval_ids = rec.approval_ids.filtered(lambda approval_line: approval_line.approver_id)
            else:
                rec.many_approval_ids = False

    many_approval_ids = fields.Many2many('approval.line', compute=_compute_approval_ids, string="Approvers")
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
            if logged_in_user.has_group("sale_multi_approval.group_approver") or logged_in_user.has_group(
                    'sale_multi_approval.group_approve_manager'):
                rec.has_sign_group = True
            else:
                rec.has_sign_group = False

    has_sign_group = fields.Boolean(string="Has Sign Group", compute=_compute_user_group)

    def action_quotation_send(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)

        #  assign the signed document to the email-wizard
        signed_doc = []
        if self.signed_xml_document:
            signed_doc.append(self.signed_xml_document.id)

        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
            #  continiuation of assign the signed document to the email-wizard
            'default_attachment_ids': signed_doc,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

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
        logged-in user is eligible or not for approving the document"""
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
                _logger.warning(f"sale_approve res: {res}")
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
                        # 'url': f"{base_url}/web#id={self.id}&model=sale.order&view_type=form"
                    }
                else:
                    if res.get('status'):
                        raise ValidationError(
                            _("Singport returned a error.\n Please contact support for assistance.\n" +
                              "Technical information: " + f"{res}"))

                    raise ValidationError(
                        _("Singport returned an unkown error.\n Please contact support for assistance."))

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


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    quotation_locked = fields.Boolean(string="Lock Quotation", related="order_id.quotation_locked")
