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
import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _inverse_main_image(self, image):
        for product in self:
            if image:
                if product.image_ids and product.image_ids[0].image_attachment_id:
                    product.image_ids[0].image_attachment_id.datas = image
                    return
                else:
                    attachment = self.env['ir.attachment'].create({
                        'name': 'Product Image for %s' % product.name,
                        'datas': image,
                    })
                if product.image_ids:
                    product.image_ids[0].write({
                        'image_attachment_id': attachment.id,
                        'storage': 'filestore',
                    })
                
                else:
                    product.image_ids = product.image_ids.create({
                        'name': product.name,
                        'image_attachment_id': attachment.id,
                        'storage': 'filestore',
                        'owner_id': product.product_tmpl_id.id,
                        'owner_model': 'product.template',
                        'product_variant_ids': [(6, 0, product.ids)]
                    })
            elif product.image_ids:
                product.image_ids = [(3, product.image_ids[0].id)]

    @api.model
    def _move_images_to_filestore(self):
        """Convert all product images to filestore images."""
        for product in self.search([('image_ids', '!=', False)]):
            for image in product.image_ids:
                if image.storage == 'db':
                    attachment = self.env['ir.attachment'].create({
                        'name': 'Product Image for %s' % product.name,
                        'datas': image.file_db_store,
                    })
                    image.write({
                        'image_attachment_id': attachment.id,
                        'storage': 'filestore',
                        'file_db_store': False,
                    })
