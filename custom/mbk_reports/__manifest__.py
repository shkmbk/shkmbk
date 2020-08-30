# -*- coding: utf-8 -*-
{
    'name': 'mbk_reports',
    'summary': 'Custom reports as per the user requirements',
    'description': 'To generate custom reports',
    'author': 'MBK Group',
    'website': 'http://www.shkmbk.ae',
    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Reports',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/wizard_bill_summary.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
