import logging
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields, _
from odoo.http import request
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"
    fill_work_and_product_description = fields.Boolean(string='Fill Product and Work description in the webshop', help="If true then people have two extra fields they have to fill in before adding a product to the cart")
   
