# -*- coding: utf-8 -*-
# Part of http://www.Mindifnosys.com See LICENSE file for full copyright and licensing details.

{
    'name': 'MIS AUH Over Ride View',
    'version': '13.0.0.3',
    'category': 'Accounting',
    'summary': """ """,
    'description': """ Used to overide the field view set based on default user group.
                    """,
    'author': "Rinto Antony",
    'website': 'http://www.Mindifnosys.com',
    'license': 'Other proprietary',
    'depends': ['account'],
    'data': [
        'security/account_move_security.xml',
        'views/account_move_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
