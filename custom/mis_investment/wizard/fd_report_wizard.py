
from odoo import fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError


class FDSummaryReport(models.TransientModel):
    _name = 'mis.auh.fdsummaryreport.wizard'
    _description = 'Fixed Deposit Summary Report'

    date_to = fields.Date(default=fields.Date.to_string(date.today()), required="1")

    def button_export_pdf(self):
        data = {}
        #raise  UserError(self.date_to+ timedelta(days=1))
        data['date_to'] = self.date_to
        report = self.env.ref(
            'mis_investment.action_fd_summary_report')
        return report.report_action(self, data=data)

