# -*- coding: utf-8 -*-

{
    'name': ' WPS Report Generation for UAE',
    'version': '13.0.1.0.0',
    'summary': 'MIS Auh WPS SIF',
    'category': 'HRM and Payroll',
    'author': 'Hafeel Salim',
    'maintainer': 'Mindinfosys FZE LLC',
    'company': 'Mindinfosys FZE LLC',
    'website': 'http://www.mindinfosys.com',
    'depends': [
        'hr',
        'hr_payroll',
        'account',
        'hr_holidays',
        ],
    'data': [
        'views/view.xml',
        'wizard/wizard.xml',
        'wizard/wizard_payroll.xml',
        'security/ir.model.access.csv',
        'report/report_menu.xml',
        'report/payroll_report.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
