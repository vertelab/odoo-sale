from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

from odoo import fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_order_deadline_default = fields.Integer(string='Days Deadline', config_parameter='sale_order_deadline_task.sale_order_deadline_default', default=14)
    deadline_max_tasks = fields.Integer(string='Max Sale Deadlines', config_parameter='sale_order_deadline_task.deadline_max_tasks', default=20)

    deadline_overview_count = fields.Integer(string='Deadline Overview Count', config_parameter='sale_order_deadline_task.deadline_overview_count', default=5)
