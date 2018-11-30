# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Vertel (<http://www.vertel.se>).
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
    'name': 'Product Color Block',
    'version': '0.1',
    'category': 'sale',
    'summary': '',
    'licence': 'AGPL-3',
    'description': """
Show color block in product list
================================
""",
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['product', 'web_widget_color'],
    'data': ['views/product_view.xml'],
    'application': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
