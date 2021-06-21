{
    'name': 'AF Sale Orders',
    'version': '12.0.0.2',
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'category': 'Sale',
    'summary': 'Price-list with links to project and activities.',
    'depends': [
        'sale',
        'project',
    ],
    'data': [
        'data/product_template.xml',
        'views/project_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
