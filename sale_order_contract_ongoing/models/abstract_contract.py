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


from odoo import api, fields, models


class ContractAbstractContract(models.AbstractModel):
    _inherit = "contract.abstract.contract"

    @api.model
    def _selection_generation_type(self):
        res = super()._selection_generation_type()
        res.append(("sale_then_invoice", "Sale and then invoice that sale"))
        return res
    

