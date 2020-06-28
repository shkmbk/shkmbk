# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import time
from datetime import date, datetime
import json
import datetime
from odoo.tools import date_utils

class MisAuhPartner1(models.Model):
    _inherit = 'res.partner'


    fax = fields.Char(string="Fax", track_visibility='onchange')

class MisAuhPartner1Bank(models.Model):
    _inherit = 'res.partner.bank'

    acc_iban_number = fields.Char('IBAN')
    account_type_id = fields.Many2one('mis.bank.accounttype', string='Account Type')
    account_customer_id = fields.Char(string='Customer ID')
    account_branch_id = fields.Many2one('mis.bank.branch', string='Bank Branch')
    account_remarks = fields.Text(string='Remarks')

class MisBank(models.Model):
    _inherit = 'account.journal'

    bank_iban_number = fields.Char(related='bank_account_id.acc_iban_number', readonly=False)

class MisBankBramch(models.Model):
    _name = 'mis.bank.branch'
    _rec_name = 'account_branch'
    _description='Bank Branch'

    account_branch=fields.Char(string='Branch')

class MisBankAccountType(models.Model):
    _name = 'mis.bank.accounttype'
    _rec_name='bank_account_type'
    _description='Bank Account Type'

    bank_account_type=fields.Char(string='Account Type')




