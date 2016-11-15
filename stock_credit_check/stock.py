# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class stock_picking(models.Model):
    _inherit='stock.picking'
    
    credit_check = fields.Boolean('Credit Check OK', compute='_get_credit_check')
    
    @api.one
    @api.depends('partner_id', 'partner_id.credit', 'partner_id.credit_limit')
    def _get_credit_check(self):
        self.credit_check = self.partner_id.credit <= self.partner_id.credit_limit

    @api.multi
    def do_transfer(self):
        res = super(stock_picking, self).do_transfer()
        if res:
            for p in self:
                if not p.credit_check:
                    self.env['mail.message'].create({
                        'body': _('The delivery was sent despite a failed credit check.'),
                        'subject': _('Ignored credit check'),
                        'author_id': self.env.user.partner_id.id,
                        'res_id': p.id,
                        'model': p._name,
                        'type': 'comment',
                    })
        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
