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

    @http.route(['/web/signport_form/<int:order_id>/<int:signport_id>/start_sign'], type='http', auth="user", website=True)
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
        auth="user",
        methods=["POST", "GET"],
	website=True,
        csrf=False,
        save_session=False
    )
    def complete_signing(self, order_id, approval_id, **res):
        user_id = request.env['res.users'].browse(request.uid)
        _logger.warning(f"returning user: {user_id.name}")
        _logger.warning(f"{request.env.user=}")
        data = {
            "relayState": res["RelayState"],
            "eidSignResponse": res["EidSignResponse"],
            "binding": res["Binding"],
        }

        api_signport = request.env.ref("rest_signport.api_signport")
        res = api_signport.sudo().signport_post(data, order_id, "/CompleteSigning", sign_type="employee")
        base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return request.redirect(f"{base_url}/web#id={order_id}&model=sale.order&view_type=form")


class SaleCustomerPortal(CustomerPortal):

    @http.route(
        ["/my/orders/<int:order_id>/download_signed_doc"],
        type="http",
        auth="user",
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
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(filecontent)),
            ('Content-Disposition', content_disposition('%s.pdf' % order_sudo.name))]

        return request.make_response(filecontent, headers=pdfhttpheaders)

    @http.route(["/trigger/signature/<int:order_id>"], type="http", auth="user", website=True, )
    def trigger_doc_signature(self, order_id, **kw):
        order_sudo = request.env['sale.order'].sudo().browse(int(order_id))
        action_id = request.env.ref('sale.action_orders', raise_if_not_found=False)
        _logger.warning(f"trigger_doc_signature: {request.env.ref('sale.action_orders', raise_if_not_found=False)=}")
        vals = {'sale_id': order_sudo.id, 'action_id': action_id, 'generate_attachment': 'yes'}
        if order_sudo.latest_pdf_export or order_sudo.signed_xml_document:
            vals.update({'generate_attachment': 'no'})
        return request.render("sale_multi_approval.signature_template", vals)
