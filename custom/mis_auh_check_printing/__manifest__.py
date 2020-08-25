# -*- coding: utf-8 -*-
{
    'name': 'MIS AUH Checks Layout',
    'version': '13.0.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Print AE Checks',
    'description': """
This module allows to print your payments on pre-printed check paper.

    """,
    'website': 'http://www.mindinfosys.com',
    'depends' : ['account_check_printing'],
    'data': [
        'data/mis_auh_check_printing.xml',
        'wizard/print_prenumbered_checks_views.xml',
        'report/print_check_adib.xml',
        'report/print_check_adcb.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
}
