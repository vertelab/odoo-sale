{
    'name': 'AF Sale Orders',
    'version': '12.0.0.2',
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'category': 'Sale',
    'summary': 'Price-list with links to project and activities.',
    'description': "This module adds 'Carreer advice' and 'Interpretor' products. When Sale order approves"
                   "with 'Carreer advice' created Project and Tasks. Also adds some fileds like start date, end date"
                   "and task numbers functionality in project and tasks.",
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
