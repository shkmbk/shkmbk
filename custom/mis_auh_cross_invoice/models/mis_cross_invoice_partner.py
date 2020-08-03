# -*- coding: utf-8 -*-
#
from odoo import models, fields, api, _

class MisAuhCrossInvoicePartner(models.Model):
    _name = 'mis.crossinvoice.partner'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
#    _inherits = {'res.partner': 'partner_id'}
    _description ='Cross Invoice Sister Companies'

    partner_id = fields.Many2one('res.partner', ondelete="cascade", required=True, string='Partner')
    account_id = fields.Many2one('account.account', string='Account',
                                 index=True, ondelete="cascade",  required=True,
                                 domain=[('deprecated', '=', False)])

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)

    _sql_constraints = [
        ('partner_id', 'unique(partner_id)', "Partner already exists!"),
    ]

class MisAuhCrossInvoiceJournal(models.Model):
    _name = 'mis.crossinvoice.journal'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
#    _inherits = {'res.partner': 'partner_id'}
    _description ='Cross Invoice Sister Companies Journal'

    name=fields.Char(string='Name', default='Cross Invoice Journal Setting')
    purchase_journal_id = fields.Many2one('account.journal', string='Purchase Journal', domain="[('type', '=', 'purchase')]",
                                      required=True)
    sales_journal_id = fields.Many2one('account.journal', string='Sales Journal', domain="[('type', '=', 'sale')]",
                                      required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)

    _sql_constraints = [
        ('purchase_journal_id, sales_journal_id', 'unique(purchase_journal_id, sales_journal_id)', "Both jounral pair already exists!"),
    ]

