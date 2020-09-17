# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    labour_card_number = fields.Char(string="Employee Card Number", size=14,
                                     help="Labour Card Number Of Employee")
    salary_card_number = fields.Char(string="Salary Account Number",size=16,
                                     help="Salary card number or account number of employee")
    iban_number = fields.Char(string="IBAN Number", size=23,  help="IBAN Number")
    agent_id = fields.Many2one('res.bank', string="Agent/Bank", help="Agent ID or bank ID of Employee")
    date_of_join = fields.Date(string="Date of Join", size=14, required=True)
    id_expiry = fields.Date(string="ID Expiry", size=14)
    passport_expiry = fields.Date(string="Passport Expiry", size=14)
    payment_method = fields.Many2one('mis.hr.paymentmethod', string="Payment Method")
    full_name = fields.Char(string="Full Name", help="As per Passport/Bank Account")
    op_eligible_days = fields.Float(string="Eligible Days", help="Opening Eligible Days for Gratuity")
    op_leave_days = fields.Float(string="Annual Leave Days",help="Opening Annual Leave Days")
    

    def write(self, vals):
        if 'labour_card_number' in vals.keys():
            if vals['labour_card_number']:
                if len(vals['labour_card_number']) < 14 and len(vals['labour_card_number'])!=0:
                    vals['labour_card_number'] = vals['labour_card_number'].zfill(14)
        if 'salary_card_number' in vals.keys():
            if vals['salary_card_number']:
                if len(vals['salary_card_number']) < 16 and len(vals['salary_card_number'])!=0:
                    vals['salary_card_number'] = vals['salary_card_number'].zfill(16)
        return super(Employee, self).write(vals)

    @api.model
    def create(self, vals):
        if 'labour_card_number' in vals.keys():
            if vals['labour_card_number']:
                if len(vals['labour_card_number']) < 14 and len(vals['labour_card_number'])!=0:
                    vals['labour_card_number'] = vals['labour_card_number'].zfill(14)
        if 'salary_card_number' in vals.keys():
            if vals['salary_card_number']:
                if len(vals['salary_card_number']) < 16 and len(vals['salary_card_number'])!=0:
                    vals['salary_card_number'] = vals['salary_card_number'].zfill(16)
        return super(Employee, self).create(vals)

class MisAuhPaymentMethod(models.Model):
    _name = 'mis.hr.paymentmethod'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Payment Method",  required=True, track_visibility='onchange')

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Payment Method already exists !"),
    ]

class Bank(models.Model):
    _inherit = 'res.bank'

    routing_code = fields.Char(string="Routing Code", size=9, required=True, help="Bank Route Code")

    def write(self, vals):
        if 'routing_code' in vals.keys():
            vals['routing_code'] = vals['routing_code'].zfill(9)
        return super(Bank, self).write(vals)

    @api.model
    def create(self, vals):
        vals['routing_code'] = vals['routing_code'].zfill(9)
        return super(Bank, self).create(vals)


class Company(models.Model):
    _inherit = 'res.company'

    employer_id = fields.Char(string="Employer ID", help="Company Employer ID")

    def write(self, vals):
        if 'company_registry' in vals:
            vals['company_registry'] = vals['company_registry'].zfill(13) if vals['company_registry'] else False
        if 'employer_id' in vals:
            vals['employer_id'] = vals['employer_id'].zfill(13) if vals['employer_id'] else False
        return super(Company, self).write(vals)

    @api.model
    def create(self, vals):
        vals['company_registry'] = vals['company_registry'].zfill(13) if vals['company_registry'] else False
        if 'employer_id' in vals:
            vals['employer_id'] = vals['employer_id'].zfill(13) if vals['employer_id'] else False
        return super(Company, self).create(vals)


