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

from timeit import default_timer as timer

class Image(models.Model):
    _inherit = "base_multi_image.image"

    storage = fields.Selection(selection_add=[('filestore', 'Filestore')])
    image_attachment_id = fields.Many2one(comodel_name='ir.attachment', string='Image attachment', help='Technical field to store image in filestore')

    @api.multi
    def _get_image_from_filestore(self):
        start = timer()
        res = self.image_attachment_id and self.image_attachment_id.datas or None
        _logger.warn('_get_image_from_filestore: %s' % (timer() - start))
        return res
