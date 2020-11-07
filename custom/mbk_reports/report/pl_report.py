from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from pytz import timezone
from dateutil.relativedelta import relativedelta
import pytz


class PL_Report(models.AbstractModel):
    _name = 'report.mbk_reports.report_pl'
    _description = "Profit and Loss Report"

    def _get_report_values(self, docids, data=None):
        year = int(data['year'])
        month = int(data['month'])
        is_detailed = data['is_detailed']
        analytic_id = data['analytic_id']
        header_name = data['header_name']
        month_from = date(year, month, 1)
        month_to = month_from + relativedelta(months=+1, day=1, days=-1)
        year_from = date(year, 1, 1)
        year_to = date(year, 12, 31)
        last_to = month_from + relativedelta(days=-1)
        last_from = last_to.replace(day=1)

        self._cr.execute("""SELECT AG.Name AS particulars,
                            SUM(CASE WHEN AML.date BETWEEN '"""+str(month_from)+"""' AND '"""+str(month_to)+"""' THEN AML.credit-AML.debit ELSE 0.00 END) AS this_month,
                            SUM(AML.credit-AML.debit) AS this_year,
                            SUM(CASE WHEN AML.date BETWEEN '"""+str(last_from)+"""' AND '"""+str(last_to)+"""' THEN AML.credit-AML.debit ELSE 0.00 END) AS last_month                            
                            FROM account_move_line AS AML 
                            INNER JOIN account_account A ON AML.account_id=A.id
                            INNER JOIN account_group AG ON A.group_id= AG.id
                            WHERE  (AML.date BETWEEN '"""+str(year_from)+"""' AND '"""+str(year_to)+"""') AND AML.company_id=3 AND A.internal_group in ('income') AND (AML.analytic_account_id = '"""+str(analytic_id)+"""' OR '"""+str(analytic_id)+"""'=0)
                            GROUP BY AG.Name""")

        income_table = self._cr.dictfetchall()

        self._cr.execute("""SELECT AG.Name AS particulars,
                            SUM(CASE WHEN AML.date BETWEEN '"""+str(month_from)+"""' AND '"""+str(month_to)+"""' THEN AML.debit-AML.credit ELSE 0.00 END) AS this_month,
                            SUM(AML.debit-AML.credit) AS this_year,
                            SUM(CASE WHEN AML.date BETWEEN '"""+str(last_from)+"""' AND '"""+str(last_to)+"""' THEN AML.debit-AML.credit ELSE 0.00 END) AS last_month                            
                            FROM account_move_line AS AML 
                            INNER JOIN account_account A ON AML.account_id=A.id
                            INNER JOIN account_group AG ON A.group_id= AG.id
                            WHERE  (AML.date BETWEEN '"""+str(year_from)+"""' AND '"""+str(year_to)+"""') AND AML.company_id=3 AND A.internal_group in ('expense') and A.user_type_id<>16 AND (AML.analytic_account_id = '"""+str(analytic_id)+"""' OR '"""+str(analytic_id)+"""'=0)
                            GROUP BY AG.Name""")

        expense_table = self._cr.dictfetchall()

        self._cr.execute("""SELECT 'Depreciation and Amortization' AS particulars,
                            SUM(CASE WHEN AML.date BETWEEN '"""+str(month_from)+"""' AND '"""+str(month_to)+"""' THEN AML.debit-AML.credit ELSE 0.00 END) AS this_month,
                            SUM(AML.debit-AML.credit) AS this_year,
                            SUM(CASE WHEN AML.date BETWEEN '"""+str(last_from)+"""' AND '"""+str(last_to)+"""' THEN AML.debit-AML.credit ELSE 0.00 END) AS last_month                            
                            FROM account_move_line AS AML 
                            INNER JOIN account_account A ON AML.account_id=A.id
                            INNER JOIN account_group AG ON A.group_id= AG.id
                            WHERE  (AML.date BETWEEN '"""+str(year_from)+"""' AND '"""+str(year_to)+"""') AND AML.company_id=3 AND A.internal_group in ('expense') and A.user_type_id=16 AND (AML.analytic_account_id = '"""+str(analytic_id)+"""' OR '"""+str(analytic_id)+"""'=0)""")

        dep_table = self._cr.dictfetchall()

        income_this_month = 0.00
        income_last_month = 0.00
        income_this_year = 0.00
        expense_this_month = 0.00
        expense_last_month = 0.00
        expense_this_year = 0.00
        dep_this_month = 0.00
        dep_last_month = 0.00
        dep_this_year = 0.00

        master_table = []

        # Opening Balance

        for rec in income_table:
            income_this_month += rec['this_month']
            income_this_year += rec['this_year']
            income_last_month += rec['last_month']

        for rec in expense_table:
            expense_this_month += rec['this_month']
            expense_this_year += rec['this_year']
            expense_last_month += rec['last_month']

        for rec in dep_table:
            dep_this_month += rec['this_month'] if rec['this_month'] else 0.00
            dep_this_year += rec['this_year'] if rec['this_year'] else 0.00
            dep_last_month += rec['last_month'] if rec['last_month'] else 0.00

        opl_this_month = income_this_month-expense_this_month
        opl_this_year = income_this_year-expense_this_year
        opl_last_month = income_last_month-expense_last_month

        particulars_0 = 'REVENUE'
        particulars_1 = 'EXPENDITURE'
        particulars_2 = 'Net Operating Income / Loss'
        particulars_3 = 'Depreciation and Amortization'
        particulars_4 = 'Net Profit / Loss'

        master_table.append({
            'particulars': particulars_0,
            'this_month': income_this_month,
            'this_year': income_this_year,
            'last_month': income_last_month,
        })
        master_table.append({
            'particulars': particulars_1,
            'this_month': expense_this_month,
            'this_year': expense_this_year,
            'last_month': expense_last_month,
        })
        master_table.append({
            'particulars': particulars_2,
            'this_month': opl_this_month,
            'this_year': opl_this_year,
            'last_month': opl_last_month,
        })
        master_table.append({
            'particulars': particulars_3,
            'this_month': dep_this_month,
            'this_year': dep_this_year,
            'last_month': dep_last_month,
        })
        master_table.append({
            'particulars': particulars_4,
            'this_month': opl_this_month-dep_this_month,
            'this_year': opl_this_year-dep_this_year,
            'last_month': opl_last_month-dep_last_month,
        })
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'account.move.line',
            'docs': master_table,
            'income_table': income_table,
            'expense_table': expense_table,
            'year': year,
            'last': last_to.strftime("%B %Y").upper(),
            'this': month_to.strftime("%B %Y").upper(),
            'is_detailed': is_detailed,
            'header_name': header_name,
        }
        return docargs
