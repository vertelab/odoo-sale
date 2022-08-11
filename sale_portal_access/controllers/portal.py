# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.osv import expression


class CustomerPortalExtended(CustomerPortal):

    def _prepare_quotations_domain(self, partner):
        default_domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel'])
        ]

        if request.env.user.has_group('base.group_portal'):
            domain = expression.OR([
                default_domain, 
                [('allowed_portal_sale_user_ids', 'in', request.env.user.ids), ('privacy_visibility', '=', 'portal'), ('state', 'in', ['sent', 'cancel'])]
            ])
        else:
            domain = expression.OR([
                default_domain, 
                [('allowed_internal_sale_user_ids', 'in', request.env.user.ids), ('privacy_visibility', 'in', ['employees', 'portal']), ('state', 'in', ['sent', 'cancel'])]
            ])
        return domain


    def _prepare_orders_domain(self, partner):
        default_domain = [
            ('state', 'in', ['sale', 'done']),
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id])
        ]
        if request.env.user.has_group('base.group_portal'):
            domain = expression.OR([
                default_domain, 
                [('allowed_portal_sale_user_ids', 'in', request.env.user.ids), ('privacy_visibility', '=', 'portal'), ('state', 'in', ['sale', 'done'])]
            ])
        else:
            domain = expression.OR([
                default_domain, 
                [('allowed_internal_sale_user_ids', 'in', request.env.user.ids), ('privacy_visibility', 'in', ['employees', 'portal']), ('state', 'in', ['sale', 'done'])]
            ])
        return domain
