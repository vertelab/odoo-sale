from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    privacy_visibility = fields.Selection([
        ('followers', 'Invited internal users'),
        ('employees', 'All internal users'),
        ('portal', 'Invited portal users and all internal users'),
    ],
    string='Visibility', required=True,
    default='portal',
    help="People to whom this sale order will be visible.\n\n"
        "- Invited internal users: when following a sale order, internal users will get access to all of its sales without distinction. "
        "Otherwise, they will only get access to the specific sale order they are following.\n "
        "The customer can still access this sales order, even if they are not explicitly part of the followers.\n\n"
        "- All internal users: all internal users can access the sales order without distinction.\n\n"
        "- Invited portal users and all internal users: all internal users can access the sales order without distinction.\n"
        "When following a sales order, portal users will get access to all without distinction.")

    

    @api.depends('allowed_internal_sale_user_ids', 'allowed_portal_sale_user_ids')
    def _compute_allowed_sales_order_users(self):
        print('_compute_allowed_sales_order_users')
        for sale in self:
            print('sale', sale)
            users = sale.allowed_internal_sale_user_ids | sale.allowed_portal_sale_user_ids
            print('_compute_allowed_users', users)
            sale.allowed_sale_user_ids = users

    def _inverse_allowed_sales_order_user(self):
        for sale in self:
            allowed_users = sale.allowed_sale_user_ids
            sale.allowed_portal_sale_user_ids = allowed_users.filtered('share')
            sale.allowed_internal_sale_user_ids = allowed_users - sale.allowed_portal_sale_user_ids

    allowed_sale_user_ids = fields.Many2many('res.users', compute=_compute_allowed_sales_order_users, inverse=_inverse_allowed_sales_order_user)

    allowed_internal_sale_user_ids = fields.Many2many('res.users', 'sales_allowed_internal_users_rel',
                                                 string="Allowed Internal Users", default=lambda self: self.env.user, domain=[('share', '=', False)])

    allowed_portal_sale_user_ids = fields.Many2many('res.users', 'sales_allowed_portal_users_rel', string="Allowed Portal Users", domain=[('share', '=', True)])