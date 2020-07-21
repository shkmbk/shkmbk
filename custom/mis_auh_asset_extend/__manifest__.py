# -*- coding: utf-8 -*-
{
    'name': 'Mis Auh Asset Extend',
    'version': '1.1.1',
    'category': 'Accounting',
    'summary': """ """,
    'description': """ Account Asset Extend
                    """,
    'author': "Sananaz Mansuri",
    'website': 'Mindifnosys.com',
    'depends': ['base','account','account_asset'],
    'data': [
        'views/account_asset_views.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
