# -*- coding: UTF-8 -*-

################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 N-Development (<https://n-development.com>).
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
################################################################################

{
    'name': 'IPF Suborder Server',
    'version': '12.0.0.3',
    'category': 'sale',
    'description': """Receives a suborder and automatically create sale.order 
and outplacement.outplacement objects.\n
v12.0.0.2 AFC-1323 Implementation of Suborder message server to respond when BÄR sends a suborder (SV: avrop) for KVL\n
v12.0.0.3 AFC-2000 added support for duplicate check.\n
""",
    'author': "N-development",
    'license': 'AGPL-3',
    'website': 'https://www.n-development.com',
    'depends': [
        'outplacement','web'
    ],
    'data': [

    ],
    'installable': True,
    'qweb': [

    ],

    'images': [
        'static/description/img.png'
    ],
}
