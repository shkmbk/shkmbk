
{
    'name': 'MIS Auh DashBoard',
    'version': '13.0.1',
    'category': 'Accounting',
    'summary': """ Dashboard Summary""",
    'description': """
                    Mis Auh Dashboard
                    """,
    'author': ' Mindinfosys.com',
#    'website': "http://www.mindinfosys.com",
    'company': 'Mindinfosys FZE LLC',
    'maintainer': 'Mindinfosys FZE LLC',
    'depends': ['base', 'account'],
    'data': [
        'views/assets.xml',
        'views/assets_investment.xml',
        'views/assets_division.xml',
        'views/dashboard_views.xml',
        'views/accounting_menu.xml',
    ],
    'qweb': [
        'static/src/xml/template.xml',
        'static/src/xml/investment_template.xml',
        'static/src/xml/division_template.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
