from odoo import fields, http, _
from odoo.http import request
import json
import logging
import base64
from odoo.exceptions import AccessError, MissingError
import binascii
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv import expression
from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    pager as portal_pager,
    get_records_pager,
)


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
        methods=["POST"],
        csrf=False,
        website=True,
    )
    def complete_signing(self, order_id, approval_id, **res):
        data = {
            "relayState": res["RelayState"],
            "eidSignResponse": res["EidSignResponse"],
            "binding": res["Binding"],
        }

        api_signport = request.env.ref("rest_signport.api_signport")
        res = api_signport.sudo().signport_post(data, order_id, "/CompleteSigning", sign_type="employee")

        order_sudo = request.env["sale.order"].sudo().browse(order_id)
        request.env["approval.line"].sudo().browse(approval_id).update({'approval_status': True})
        base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return request.redirect(f"{base_url}/web#id={order_id}&model=sale.order&view_type=form")