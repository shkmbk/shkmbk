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

class Mbk_Audit_Trail_Wizard(models.TransientModel):
    _name = 'mbk.wizard.report.audit_trail'
    _description = "Audit Trail Report"

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))

    from_date = fields.Date(default=fields.Date.to_string(date.today()), string='From', required=True)
    to_date = fields.Date(default=fields.Date.to_string(date.today()), string='To Date', required=True)
    user_id = fields.Many2one('res.users', "User")
    is_include_auto = fields.Boolean(string="Auto Entries", default=False)


    def print_audit_trail_report_pdf(self):
        data = {'from_date': self.from_date,
                'to_date': self.to_date,
                'user_id': self.user_id.id,
                'is_include_auto': self.is_include_auto,
                'header_period': '('+self.from_date.strftime("%d/%m/%Y") + ' - ' + self.to_date.strftime("%d/%m/%Y")+')'}
        report = self.env.ref('mbk_reports.audit_trail_report_pdf')
        return report.report_action(self, data=data)

    def print_gratuity_report_xls(self):
        raise UserError("In Progress, Comeback Later")