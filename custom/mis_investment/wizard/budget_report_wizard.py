from odoo import fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class BudgetReportWizard(models.TransientModel):
    _name = 'mbk.budget.wizard'
    _description = 'Fund Flow Budget Report'

    date_from = fields.Date(string="From Date", default='2020-06-01', required="1", )
    date_to = fields.Date(string="To Date", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required="1")
    year = fields.Selection([(str(num), str(num)) for num in range(2020, (datetime.now().year) + 2)], default=str(datetime.now().year),
                            required="1")

    def button_export_pdf(self):
        data = {'date_from': self.date_from, 'date_to': self.date_to, 'year': self.year,
                'header_period': self.date_from.strftime("%d/%m/%Y") + ' - ' + self.date_to.strftime("%d/%m/%Y")}
        report = self.env.ref('mis_investment.action_budget_report')
        return report.report_action(self, data=data)
