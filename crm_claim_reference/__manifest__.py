# -*- coding: utf-8 -*-
{
    'name': "crm_claim_reference",
    'summary': """
        Reklamationsärende
    """,
    'description': """
        Long description of module's purpose
    """,
    'author': "Vertel AB",
    'website': "http://www.vertel.se",
    'category': 'Claim',
    'version': '14.0.0.0.1',
    'depends': ['sale','bi_crm_claim','crm'],
    'data': [
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/crm_claim_menu.xml",
    ],
    "installable": True,
}
