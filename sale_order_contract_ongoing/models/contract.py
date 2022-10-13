# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


from werkzeug.urls import url_encode

import logging
_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "contract.contract"

    def _compute_sale_invoice_count(self):
        for rec in self:
            rec.sale_invoice_count = len(rec._get_related_sales_invoices())

    sale_invoice_count = fields.Integer(string="Sales Invoice", compute=_compute_sale_invoice_count)

    def action_recurring_sales_invoice(self):
        if not self._get_related_sales():
            sales_values = self._prepare_recurring_sales_values()
            sale_orders = self.env["sale.order"].create(sales_values)
            sale_orders.action_confirm()
        self._recurring_invoice()

    def _recurring_invoice(self):
        sale_order = self._get_related_sales()
        if sale_order:
            payment = self.env['sale.advance.payment.inv'].with_context({
                'active_model': 'sale.order',
                'active_ids': [sale_order.id],
                'active_id': sale_order.id,
            }).create({
                'advance_payment_method': 'delivered'
            })
            payment.create_invoices()
        self._compute_recurring_next_date()
        invoice_ids = self._get_related_sales().invoice_ids.filtered(lambda invoice: invoice.state == 'draft')
        invoice_ids.action_post()

    def action_show_sale_invoices(self):
        self.ensure_one()
        tree_view = self.env.ref("account.view_invoice_tree", raise_if_not_found=False)
        form_view = self.env.ref("account.view_move_form", raise_if_not_found=False)
        ctx = dict(self.env.context)
        if ctx.get("default_contract_type"):
            ctx["default_move_type"] = (
                "out_invoice"
                if ctx.get("default_contract_type") == "sale"
                else "in_invoice"
            )
        action = {
            "type": "ir.actions.act_window",
            "name": "Invoices",
            "res_model": "account.move",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [("id", "in", self._get_related_sales().invoice_ids.ids)],
            "context": ctx,
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action

    def _get_related_sales_invoices(self):
        self.ensure_one()
        invoices = (
            self.env["account.move"]
            .search(
                [
                    (
                        "id",
                        "in",
                        self._get_related_sales().invoice_ids.ids,
                    )
                ]
            )
        )
        # we are forced to always search for this for not losing possible <=v11
        # generated invoices
        invoices |= self.env["account.move"].search([("old_contract_id", "=", self.id)])
        return invoices

    def _cron_recurring_create_sale_invoice(self):
        sale_invoice_ids = self.env["contract.contract"].search([
            ("generation_type", "=", "sale_then_invoice"),
            ("recurring_next_date", "=", fields.Date.today())
        ])

        for inv in sale_invoice_ids:
            try:
                inv._recurring_invoice()
            except Exception as e:
                inv.message_post(body=e)


