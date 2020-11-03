{
    'name': 'AF Sale Orders',
    'version': '12.0.0.0',
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'category': 'Sale',
    'summary': 'Price-list with links to project and activities.',
    'description': "This module adds 'Carreer advice' and 'Interpretor' products. When Sale order approves"
                   "with these products created Project and Tasks.",
    'depends': [
        'sale',
        'project',
    ],
    'data': [
        'data/product_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
