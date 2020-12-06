from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class PayrollSummaryReport(models.AbstractModel):
    _name = "report.mis_investment.report_mbk_hr_document"
    _description = "Employee And Payroll Summary Report"

    def _get_report_values(self, docids, data=None):
        from_date = data['date_from']
        to_date = data['date_to']
        year = int(data['year'])
        month = int(data['month'])
        year_from = date(year, month, 1)
        year_to = year_from + relativedelta(months=+1, day=1, days=-1)
        obj_hr = self.env['mbk.hr.line'].search(
            [('mbk_hr_id.state', '=', 'posted'), ('to_date', '>=', year_from), ('to_date', '<=', year_to)],
            order='to_date, sl_no', limit=1)
        if not obj_hr:
            raise UserError('No records found in selected parameter')

        self._cr.execute("""SELECT AAA.id,AAA.name AS Company, SUM(HRL.opening_nos) AS opening_nos, SUM(HRL.new_nos) AS new_nos, SUM(HRL.exit_nos) AS exit_nos, SUM(HRL.closing_nos) AS closing_nos, SUM(HRL.salary) AS salary,
                                SUM(HRL.deductions) AS deductions, SUM(leave_salary) AS leave_salary, SUM(net_salary) AS net_salary
                                FROM mbk_hr HR 
                                INNER JOIN mbk_hr_line HRL ON HR.id=HRL.mbk_hr_id
                                INNER JOIN account_analytic_account AAA ON AAA.id=HRL.analytic_account_id
                            WHERE HR.state='posted' AND HR.company_id=3 AND (HR.date_to BETWEEN '"""+str(year_from)+"""' AND '"""+str(year_to)+"""') 
                            GROUP BY AAA.name,AAA.id
                            ORDER BY 1""")
        master_table = self._cr.dictfetchall()

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'mbk.hr',
            'docs': master_table,
            'header_period': data['header_period'],
            'from_date': year_from.strftime("%d/%m/%Y"),
            'to_date': year_to.strftime("%d/%m/%Y"),
        }
        return docargs
