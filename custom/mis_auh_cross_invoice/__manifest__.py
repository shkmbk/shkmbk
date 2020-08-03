
{
    'name': 'MIS-AUH Cross Invoice',
    'version': '13.0.0.1',
    'summary': """Cross Invoice to the Sister company""",
    'category': 'Invoice',
    'author': 'Hafeel Salim, hafeel.salim@mindinfosys.com',
    'company': 'mindinfosys.com, UAE',
    'description': 'Accounting Customization',
    'website': 'www.mindinfosys.com',
    'depends': ['base','account', 'purchase', 'sale', 'account_asset', 'analytic','stock',],
    'data': [
        'data/crossinvoice_data.xml',
        'wizard/mis_crossinvoice_bills_views.xml',
        'views/mis_cross_invoice.xml',
        'views/mis_cross_invoice_partner_config.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}