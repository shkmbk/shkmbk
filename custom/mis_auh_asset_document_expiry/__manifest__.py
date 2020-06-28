# -*- coding: utf-8 -*-

# Part of Mindifnosys.com See LICENSE file for full copyright and licensing details.
{
    'name': 'Asset Documents Expiry',
    'version': '13.0.0.1',
    'summary': """Manages Asset Documents With Expiry Notifications.""",
    'description': """Manages Asset Related Documents with Expiry Notifications.""",
    'category': 'Generic Modules/Human Resources',
    'author': 'Sananaz Mansuri',
    'website': 'http://www.Mindifnosys.com',
    'depends': ['base','account','account_asset'],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_asset_document_view.xml',
        'views/document_type_view.xml',
        'views/asset_document_view.xml',
    ],
    'license': 'Other proprietary',
    'installable': True,
    'auto_install': False,
    'application': False,
}
