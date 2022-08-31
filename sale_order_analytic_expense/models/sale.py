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

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.depends('product_id')
    def _compute_qty_delivered_method(self):
        """ Stock module compute delivered qty for product [('type', 'in', ['consu', 'product'])]
            For SO line coming from expense, no picking should be generate: we don't manage stock for
            thoses lines, even if the product is a storable.
        """
        super(SaleOrderLine, self)._compute_qty_delivered_method()

        for line in self:
            if line.product_id.is_analytic_cost:
                line.qty_delivered_method = 'analytic'

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    

    @api.depends('timesheet_ids', 'company_id.timesheet_encode_uom_id')
    def _compute_timesheet_total_duration(self):
        for sale_order in self:
            timesheets = sale_order.timesheet_ids if self.user_has_groups('hr_timesheet.group_hr_timesheet_approver') else sale_order.timesheet_ids.filtered(lambda t: t.user_id.id == self.env.uid)
            total_time = 0.0
            uom_category_time_ids = self.env['uom.category'].search([('name', '=', 'Working Time')], limit=1)
            for timesheet in timesheets.filtered(lambda t: not t.non_allow_billable and t.product_uom_id.category_id == uom_category_time_ids):
                # Timesheets may be stored in a different unit of measure, so first we convert all of them to the reference unit
                total_time += timesheet.unit_amount * timesheet.product_uom_id.factor_inv
            # Now convert to the proper unit of measure
            total_time *= sale_order.timesheet_encode_uom_id.factor
            sale_order.timesheet_total_duration = total_time

    
    def action_view_timesheet(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sale_timesheet.timesheet_action_from_sales_order")
        action['context'] = {
            'search_default_billable_timesheet': True
        }  # erase default filters
        uom_category_time_ids = self.env['uom.category'].search([('name', '=', 'Working Time')], limit=1)
        if self.timesheet_count > 0:
            action['domain'] = [('so_line', 'in', self.order_line.ids), ('product_uom_id.category_id', '=', uom_category_time_ids.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action



    # @api.depends('analytic_account_id.line_ids') TODO IMPLEMENT
    # def _compute_other_analytic_ids(self):
    #     for order in self:
    #         if order.analytic_account_id:
    #             order.timesheet_ids = self.env['account.analytic.line'].search(
    #                 [('so_line', 'in', order.order_line.ids),
    #                     ('amount', '<=', 0.0),
    #                     ('project_id', '!=', False)])
    #         else:
    #             order.timesheet_ids = []
    #         order.timesheet_count = len(order.timesheet_ids)

    # other_analytic_ids = fields.Many2many('account.analytic.line', compute='_compute_other_analytic_ids', string='Timesheet activities associated to this sale')
    # other_analytic_count = fields.Float(string='Timesheet activities', compute='_compute_other_analytic_ids', groups="hr_timesheet.group_hr_timesheet_user")
    # def action_view_other_analytic_lines(self):
    #     self.ensure_one()
    #     action = self.env["ir.actions.actions"]._for_xml_id("sale_timesheet.timesheet_action_from_sales_order")
    #     action['context'] = {
    #         'search_default_billable_timesheet': True
    #     }  # erase default filters
    #     uom_category_time_ids = self.env['uom.category'].search([('name', '=', 'Working Time')], limit=1)
    #     if self.timesheet_count > 0:
    #         action['domain'] = [('so_line', 'in', self.order_line.ids), ('product_uom_id.category_id', '!=', uom_category_time_ids.ids)]
    #     else:
    #         action = {'type': 'ir.actions.act_window_close'}
    #     return action


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_analytic_cost = fields.Boolean()