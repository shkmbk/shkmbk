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
        'wizard/wizard_stock_details.xml',
        'wizard/wizard_stock_summary.xml',
        'wizard/wizard_share_summary.xml',
        'wizard/wizard_share_details.xml',
        'wizard/wizard_gratuity_report.xml',
        'wizard/wizard_farm_stock_summary.xml',        
        'report/report_menu.xml',
        'report/stock_details_template.xml',
        'report/farmstock_details_template.xml',
        'report/gratuity_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
