# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo.tools import date_utils
import xlsxwriter
import base64
from odoo import fields, models, api, _
from io import BytesIO
from pytz import timezone
import pytz

class Mbkannualleave_Wizard(models.TransientModel):
    _name = 'mbk.wizard.report.annualleave'
    _description = "Annual Leave Report"

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))

    ason_date = fields.Date(default=fields.Date.to_string(date.today()), string='As On Date', required=True)
    employee_id = fields.Many2one('hr.employee',"Employee")
    hr_department_ids = fields.Many2many('hr.department', string='Department(s)')
    category_ids = fields.Many2many('hr.employee.category', string='Tags')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')    


    def print_annualleave_report_pdf(self):
        data = {}
        data['ason_date'] = self.ason_date
        data['employee_id'] = self.employee_id.id
        tmpdate = self.ason_date
        data['hr_department_ids'] = self.hr_department_ids.id
        data['category_ids'] = self.category_ids.id
        data['analytic_account_id'] = self.analytic_account_id.id
        data['analytic_tag_ids'] = self.analytic_tag_ids.id        
        data['header_date'] = tmpdate.strftime("%d-%m-%Y")
        report = self.env.ref('mbk_reports.annualleave_report_pdf')        
        return report.report_action(self, data=data)    
    def print_annualleave_report_xls(self):
        raise UserError("In Progress, Comeback Later")
     
        