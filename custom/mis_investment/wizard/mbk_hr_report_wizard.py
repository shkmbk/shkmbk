from odoo import fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import calendar


class HRReportWizard(models.TransientModel):
    _name = 'mbk.hr.wizard'
    _description = 'Employee And Payroll Summary For The Month'

    date_from = fields.Date(string="From Date", default='2020-06-01', required="1", )
    date_to = fields.Date(string="Month", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required="1")
    year = fields.Selection([(str(num), str(num)) for num in range(2020, (datetime.now().year) + 2)], default=str(datetime.now().year),
                            required="1")
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], string='Month', default=str((date.today() + relativedelta(months=-1)).month), required="1")

    def button_export_pdf(self):
        header_period = calendar.month_name[int(self.month)] + ' ' + self.year
        data = {'date_from': self.date_from, 'date_to': self.date_to, 'year': self.year, 'month': self.month,
                'header_period': header_period.upper()}
        report = self.env.ref('mis_investment.action_mbk_hr_report')
        return report.report_action(self, data=data)
