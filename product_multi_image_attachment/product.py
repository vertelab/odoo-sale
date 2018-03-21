# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, fields, _
from openerp import tools
from openerp.osv import orm
from openerp.osv import fields as old_fields
import base64

import logging
_logger = logging.getLogger(__name__)

class ir_attachment(models.Model):
    _inherit = "ir.attachment"

    sequence = fields.Integer()

class ProductTemplate(models.Model):
    _inherit = "product.template"

    image_main_id = fields.Many2one(comodel_name='ir.attachment',string="Main image",compute='_get_image_main_id',store=True)
    image_main_medium_id = fields.Many2one(comodel_name='ir.attachment',string="Medium image",compute='_get_image_main_id',store=True)
    image_main_small_id = fields.Many2one(comodel_name='ir.attachment',string="Small image",compute='_get_image_main_id',store=True)

    image_attachment_ids = fields.Many2many(string='Images', comodel_name='ir.attachment')
    image_main = fields.Binary(compute='_get_multi_image')
    image_main_medium = fields.Binary(compute='_get_multi_image')
    image_main_small = fields.Binary(compute='_get_multi_image')

    @api.one
    @api.depends('image_attachment_ids', 'product_variant_ids.image_attachment_ids')
    def _get_image_main_id(self):
        _logger.warn('%s._get_image_main_id: %s' % (self, self.image_attachment_ids))
        if self.image_attachment_ids:
            self.image_main_id = self.image_attachment_ids.sorted(lambda r: r.sequence)[0]
        else:
            images = self.product_variant_ids.filtered(lambda v: v.default_variant == True).mapped('image_attachment_ids').sorted(lambda r: r.sequence)
            if not images:
                images = self.product_variant_ids.mapped('image_attachment_ids').sorted(lambda r: r.sequence)
            self.image_main_id = images and images[0]
        #~ raise Warning(self.image_main_id.datas)
        #~ images = tools.image_get_resized_images(base64.encodestring(self.image_main_id.datas))
        if not self.image_main_medium_id:
            self.image_main_medium_id = self.env['ir.attachment'].create({
                        'name': '%s_medium' % self.name,
                        'res_name': self.name,
                        'res_model': self._name,
                        'res_id': self.id,
                        #~ 'datas': base64.encodestring(images['image_medium']),
                        'datas': self.image_main_id.datas,
                        'datas_fname': '%s_medium' % self.name ,
                    }).id
        else:
            #~ self.image_main_medium_id.datas = base64.encodestring(images['image_medium'])
            self.image_main_medium_id.datas = base64.encodestring(self.image_main_id.datas)
        if not self.image_main_small_id:   
            self.image_main_small_id = self.env['ir.attachment'].create({
                        'name': '%s_small' % self.name,
                        'res_name': self.name,
                        'res_model': self._name,
                        'res_id': self.id,
                        #~ 'datas': base64.encodestring(images['image_small']),
                        'datas': self.image_main_id.datas,
                        'datas_fname': '%s_small' % self.name ,
                    }).id
        else:
            #~ self.image_main_small_id.datas = base64.encodestring(images['image_small'])
            self.image_main_small_id.datas = base64.encodestring(self.image_main_id.datas)

    @api.one
    def _get_multi_image(self):
        """Get the main image for this object.
        """
        self.image_main = self.image_main_id.datas
        self.image_main_medium = self.image_main_medium_id.datas
        self.image_main_small = self.image_main_small_id.datas

    @api.one
    def get_image_attachment_ids(self):
        return self.image_attachment_ids.mapped('id') + self.product_variant_ids.mapped('image_attachment_ids').mapped('id')

class ProductTemplateOld(orm.Model):
    """Reference core image old_fields to multi-image variants.

    It is needed to use v7 api here because core model old_fields use the ``multi``
    attribute, that has no equivalent in v8, and it needs to be disabled or
    bad things will happen. For more reference, see
    https://github.com/odoo/odoo/issues/10799
    """
    _inherit = "product.template"
    _columns = {
        "image": old_fields.related(
            "image_main",
            type="binary",
            store=False,
            multi=False),
        "image_medium": old_fields.related(
            "image_main_medium",
            type="binary",
            store=False,
            multi=False),
        "image_small": old_fields.related(
            "image_main_small",
            type="binary",
            store=False,
            multi=False)
    }

class ProductProduct(models.Model):
    _inherit = "product.product"

    v_image_main_id = fields.Many2one(comodel_name='ir.attachment',string="Main image",compute='_get_image_main_id',store=True)
    v_image_main_medium_id = fields.Many2one(comodel_name='ir.attachment',string="Medium image",compute='_get_image_main_id',store=True)
    v_image_main_small_id = fields.Many2one(comodel_name='ir.attachment',string="Small image",compute='_get_image_main_id',store=True)
    image_attachment_ids = fields.Many2many(string='Images', comodel_name='ir.attachment')
    image_main = fields.Binary(compute='_get_multi_image')
    image_main_medium = fields.Binary(compute='_get_multi_image')
    image_main_small = fields.Binary(compute='_get_multi_image')

    @api.one
    @api.depends('image_attachment_ids', 'product_tmpl_id.image_attachment_ids')
    def _get_image_main_id(self):
        _logger.warn('%s._get_image_main_id: %s' % (self, self.image_attachment_ids))
        if self.image_attachment_ids:
            self.v_image_main_id = self.image_attachment_ids[0]
        else:
            self.v_image_main_id = self.product_tmpl_id.image_attachment_ids and self.product_tmpl_id.image_attachment_ids.sorted(lambda r: r.sequence)[0]
        images = tools.image_get_resized_images(self.image_main_id.datas)
        if not self.v_image_main_medium_id:
            self.v_image_main_medium_id = self.env['ir.attachment'].create({
                        'name': '%s_medium' % self.name,
                        'res_name': self.name,
                        'res_model': self._name,
                        'res_id': self.id,
                        #~ 'datas': base64.encodestring(images['image_medium']),
                        'datas': base64.encodestring(self.v_image_main_id.datas),
                        'datas_fname': '%s_medium' % self.name ,
                    }).id
        else:
            #~ self.image_main_medium_id.datas = base64.encodestring(images['image_medium'])
            self.v_image_main_medium_id.datas = base64.encodestring(self.v_image_main_id.datas)
        if not self.v_image_main_small_id:   
            self.v_image_main_small_id = self.env['ir.attachment'].create({
                        'name': '%s_small' % self.name,
                        'res_name': self.name,
                        'res_model': self._name,
                        'res_id': self.id,
                        #~ 'datas': base64.encodestring(images['image_small']),
                        'datas': base64.encodestring(self.v_image_main_id.datas),
                        'datas_fname': '%s_small' % self.name ,
                    }).id
        else:
            #~ self.image_main_small_id.datas = base64.encodestring(images['image_small'])
            self.v_image_main_small_id.datas = base64.encodestring(self.v_image_main_id.datas)


    @api.one
    def get_image_attachment_ids(self):
        return self.image_attachment_ids.mapped('id') + self.product_tmpl_id.image_attachment_ids.mapped('id')
    
    @api.one
    def _get_multi_image(self):
        """Get the main image for this object.
        """
        self.v_image_main = self.image_main_id.datas
        self.v_image_main_medium = self.image_main_medium_id.datas
        self.v_image_main_small = self.image_main_small_id.datas

class ProductProductOld(orm.Model):
    """It is needed to use v7 api here because core model fields use the
    ``multi`` attribute, that has no equivalent in v8, and it needs to be
    disabled or bad things will happen. For more reference, see
    https://github.com/odoo/odoo/issues/10799

    Needed for getting the correct data in the inheritance chain. Probably
    in v10 this won't be needed as the inheritance has been globally
    redesigned.
    """

    _inherit = "product.product"
    _columns = {
        "image": old_fields.related(
            "image_main", type="binary", store=False, multi=False),
        "image_medium": old_fields.related(
            "image_main_medium", type="binary", store=False, multi=False),
        "image_small": old_fields.related(
            "image_main_small", type="binary", store=False, multi=False)
    }
