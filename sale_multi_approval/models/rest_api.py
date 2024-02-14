from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)
import requests
import werkzeug
from odoo.http import request
import json
import base64
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import uuid
import re
from bs4 import BeautifulSoup
import requests


class RestApiSignport(models.Model):
    _inherit = "rest.api"

    def post_sign_sale_order(self, ssn, order_id, access_token, message=False, sign_type="customer", approval_id=False):
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
