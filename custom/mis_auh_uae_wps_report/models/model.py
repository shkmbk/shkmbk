# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    labour_card_number = fields.Char(string="Employee Card Number", size=14, required=False,
                                     help="Labour Card Number Of Employee")
    salary_card_number = fields.Char(string="Salary Account Number", size=16, required=False,
                                     help="Salary card number or account number of employee")
    iban_number = fields.Char(string="IBAN Number", size=23, required=False, help="IBAN Number")                                     
    agent_id = fields.Many2one('res.bank', string="Agent/Bank", required=False, help="Agent ID or bank ID of Employee")
    date_of_join = fields.Date(string="Date of Join", size=14, required=True)
    id_expiry = fields.Date(string="ID Expiry", size=14, required=False)
    passport_expiry = fields.Date(string="Passport Expiry", size=14, required=False)
    

    def write(self, vals):
        if 'labour_card_number' in vals.keys():
            if len(vals['labour_card_number']) < 14 and len(vals['salary_card_number'])!=0:
                vals['labour_card_number'] = vals['labour_card_number'].zfill(14)
        if 'salary_card_number' in vals.keys():
            if len(vals['salary_card_number']) < 16 and len(vals['salary_card_number'])!=0:
                vals['salary_card_number'] = vals['salary_card_number'].zfill(16)
        return super(Employee, self).write(vals)

    @api.model
    def create(self, vals):
        if 'labour_card_number' in vals.keys():
            if len(vals['labour_card_number']) < 14 and len(vals['salary_card_number'])!=0:
                vals['labour_card_number'] = vals['labour_card_number'].zfill(14)
        if 'salary_card_number' in vals.keys() and len(vals['salary_card_number'])!=0:
            if len(vals['salary_card_number']) < 16:
                vals['salary_card_number'] = vals['salary_card_number'].zfill(16)
        return super(Employee, self).create(vals)


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

