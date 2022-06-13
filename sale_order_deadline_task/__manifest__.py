# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2020- Vertel AB (<http://vertel.se>).
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
{
    'name': 'Task Sale Order DeadLine',
    'version': '14.0.1.0',
    'license': 'AGPL-3',
    'author': ' Vertel AB',
    'website': 'https://vertel.se',
    'category': 'sale',
    'depends': ['sale_management', 'sale_project', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/res_config_settings.xml'
    ],
    'installable': 'True',
    'application': 'False',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
