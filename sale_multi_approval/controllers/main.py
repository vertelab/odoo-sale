from odoo import fields, http, _, SUPERUSER_ID
from odoo.http import request
import json
import logging
import base64
from odoo.exceptions import AccessError, MissingError
from odoo.addons.web.controllers.main import content_disposition, ensure_db
import binascii
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv import expression
from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    pager as portal_pager,
    get_records_pager,
)
from odoo.addons.sale.controllers.portal import CustomerPortal


_logger = logging.getLogger(__name__)


class SaleMultiApproval(http.Controller):

    @http.route(['/web/signport_form/<int:order_id>/<int:signport_id>/start_sign'],
        type='http',
        auth="none",
    )
    def start_sign(self, order_id, signport_id, **kw):

        signport_request = request.env["signport.request"].sudo().browse(signport_id)
        values = {
            'relay_state': signport_request.relay_state,
            'eid_sign_request': signport_request.eid_sign_request,
            'binding': signport_request.binding,
            'signing_service_url': signport_request.signing_service_url,
        }
        return request.render("sale_multi_approval.signport_form", values)

    @http.route(
        ["/web/<int:order_id>/<int:approval_id>/sign_complete"],
        type="http",
        auth="public",
        methods=["POST", "GET"],
        csrf=False,
        website=True,
    )
    def complete_signing(self, order_id, approval_id, **res):
        _logger.warning(f"complete_signing first res: {res}")
        data = {
            "relayState": res["RelayState"],
            "eidSignResponse": res["EidSignResponse"],
            "binding": res["Binding"],
        }

        api_signport = request.env.ref("rest_signport.api_signport")
        res = api_signport.sudo().signport_post(data, order_id, "/CompleteSigning", sign_type="employee")
        _logger.warning(f"complete_signing second res: {res}")
        base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return request.redirect(f"{base_url}/web#id={order_id}&model=sale.order&view_type=form")


class SaleCustomerPortal(CustomerPortal):

    @http.route(
        ["/my/orders/<int:order_id>/download_signed_doc"],
        type="http",
        auth="public",
        website=True,
    )
    def download_signed_order_doc(self, order_id, access_token=None, **kw):
        """Process user's consent acceptance or rejection."""
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        filecontent = base64.b64decode(order_sudo.signed_xml_document.datas)
        content_type = ["Content-Type", "application/xml"]
        disposition_content = [
            "Content-Disposition",
            content_disposition(order_sudo.name),
        ]
        return request.make_response(filecontent, [content_type, disposition_content])

    @http.route(["/trigger/signature/<int:order_id>"], type="http", auth="public", website=True,)
    def trigger_doc_signature(self, order_id, access_token=None, **kw):
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
            print(order_sudo)
        except (AccessError, MissingError):
            return request.redirect('/web')
        return request.render("sale_multi_approval.signature_template", {'sale_id': order_sudo.id})

