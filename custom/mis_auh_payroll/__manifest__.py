# -*- coding: utf-8 -*-
# Part of http://www.Mindifnosys.com See LICENSE file for full copyright and licensing details.

{
    'name': 'MIS AUH Payroll',
    'version': '13.0.0.2',
    'category': 'Accounting',
    'summary': """ """,
    'description': """ Salary Rule for unpaid leave.
                    """,
    'author': "Sananaz Mansuri",
    'website': 'http://www.Mindifnosys.com',
    'license': 'Other proprietary',
    'depends': ['hr_payroll'],
    'data': [
        'views/mis_payslip_run_views.xml',
#        'wizard/hr_payroll_payslips_by_employees_views.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
