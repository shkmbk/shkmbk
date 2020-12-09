from odoo import fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import calendar


class FEReportWizard(models.TransientModel):
    _name = 'mbk.fe.wizard'
    _description = 'Family Expense Report'

    from_date = fields.Date(string='From Date', required=True, default='2020-06-01')
    to_date = fields.Date(string="To Date", default=fields.Date.to_string(date.today()), required=True)
    analytic_id = fields.Many2one('account.analytic.tag', string="Member", domain="[('analytic_tag_group', '=', 42)]")

    def button_export_pdf(self):
        data = {'from_date': self.from_date,
                'to_date': self.to_date,
                'header_period': '('+self.from_date.strftime("%d/%m/%Y") + ' - ' + self.to_date.strftime("%d/%m/%Y")+')', 'analytic_id': int(self.analytic_id.id)}
        report = self.env.ref('mbk_reports.fe_report')
        return report.report_action(self, data=data)

    def button_summary(self):
        data = {'from_date': self.from_date,
                'to_date': self.to_date,
                'header_period': '('+self.from_date.strftime("%d/%m/%Y") + ' - ' + self.to_date.strftime("%d/%m/%Y")+')'}
        report = self.env.ref('mbk_reports.fe_summary_report')
        return report.report_action(self, data=data)
