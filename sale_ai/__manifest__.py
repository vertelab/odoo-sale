# -*- coding: utf-8 -*-
{
    'name': 'Sale: AI Bridge',
    'version': '18.0.1.0.0',
    'summary': 'Session context for sale.order + OKF indexing',
    'category': 'Sales',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'description': """
        Bridge between sale.order and the AI core.

        CONTEXT: a session that works with a sale.order must know which
        order and which customer it works with — otherwise cost context,
        lineage and memory attach to nothing. The domain fields live here,
        not in ai_agent_core: the core stays domain-free, exactly as
        project_ai does it for project.task.

        OKF: a quotation is knowledge — what the customer ordered, at what
        price, under what terms. `sale.order` inherits ai.okf.indexable.mixin
        so it becomes an OKF concept in the company scope. The order LINES
        are not indexed separately: they are carried by the order summary.
        Twenty lines times ten thousand orders would be two hundred thousand
        concepts of noise.

        ACCESS: the concept is company knowledge, but access follows the
        order's read rights. A quotation a user may not read must not be
        injected.
    """,
    'depends': [
        'sale',
        'ai_agent_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/okf_artifact_types_sale.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
