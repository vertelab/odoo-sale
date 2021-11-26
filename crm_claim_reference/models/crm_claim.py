# -*- coding: utf-8 -*-

# ~ import odoo
from odoo import api, fields, models, modules, _
from odoo.exceptions import ValidationError


class CrmClaim(models.Model):
    _inherit = 'crm.claim'

    @api.model
    def _reference_models(self):
        obj = self.env['res.request.link']
        res = obj.search_read(fields=['obj','name'])
        return [(r['obj'], r['name']) for r in res]
        
    ref = fields.Reference(
        string='Reference',
        selection='_reference_models',
    )


class ResRequestLink(models.Model):
    _name = 'res.request.link'
    _description = 'request'

    name = fields.Char(string='Name', required=True)
    obj = fields.Selection(
        string='Object',
        required=True,
        selection='_models',
    )

    def _models(self):
        models = self.env['ir.model'].sudo().search([('state','!=','manual')])
        return [(model.model, model.model + ' - ' + model.name)
            for model in models
            if not model.model.startswith('ir.')
        ]
