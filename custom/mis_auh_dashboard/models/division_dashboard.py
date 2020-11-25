# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

from odoo import models, api
from odoo.http import request


class DivisionDashBoard(models.Model):
    _inherit = 'account.move'

    # function to Header P&L values
    @api.model
    def get_division_profit(self, division_id):

        self._cr.execute("""SELECT date FROM account_move WHERE state='posted' and company_id=3 order by date desc,id limit 1""")
        last_entry = self._cr.dictfetchall()
        if last_entry:
            last_entry_date = last_entry[0]['date']
        else:
            last_entry_date = date.today() + relativedelta(months=-1, day=1)

        analytic_id = int(division_id)
        month_from = last_entry_date.replace(day=1)
        month_to = month_from + relativedelta(months=+1, day=1, days=-1)
        last_to = month_from + relativedelta(days=-1)
        last_from = last_to.replace(day=1)
        year_from = date(month_to.year, 1, 1)
        year_to = date(month_to.year, 12, 31)
        header = month_to.strftime("%B %Y").upper()

        self._cr.execute("""SELECT  SUM(AML.credit-AML.debit) AS pl_this_year,
                            SUM(CASE WHEN AML.date BETWEEN '"""+str(month_from)+"""' AND '"""+str(month_to)+"""' THEN AML.credit-AML.debit ELSE 0.00 END) AS pl_this_month,                           
                            SUM(CASE WHEN A.internal_group='income' THEN AML.credit-AML.debit ELSE 0.00 END) AS income_this_year,
                            SUM(CASE WHEN A.internal_group='income' AND AML.date BETWEEN '"""+str(month_from)+"""' AND '"""+str(month_to)+"""' THEN AML.credit-AML.debit ELSE 0.00 END) AS income_this_month,
                            SUM(CASE WHEN A.internal_group='expense' THEN AML.debit-AML.credit ELSE 0.00 END) AS expense_this_year,
                            SUM(CASE WHEN A.internal_group='expense' AND AML.date BETWEEN '"""+str(month_from)+"""' AND '"""+str(month_to)+"""' THEN AML.debit-AML.credit ELSE 0.00 END) AS expense_this_month,
                            SUM(CASE WHEN A.user_type_id<>16 THEN AML.credit-AML.debit ELSE 0.00 END) AS opl_this_year,
                            SUM(CASE WHEN A.user_type_id<>16 AND AML.date BETWEEN '"""+str(month_from)+"""' AND '"""+str(month_to)+"""' THEN AML.credit-AML.debit ELSE 0.00 END) AS opl_this_month,
                            '"""+str(header)+"""' AS header
                            FROM account_move_line AS AML 
                            INNER JOIN account_account A ON AML.account_id=A.id
                            INNER JOIN account_group AG ON A.group_id= AG.id
                            WHERE  AML.parent_state='posted' AND (AML.date BETWEEN '"""+str(year_from)+"""' AND '"""+str(year_to)+"""') AND AML.company_id=3 AND A.internal_group in ('income','expense') AND (AML.analytic_account_id = '"""+str(analytic_id)+"""' OR '"""+str(analytic_id)+"""'=0)""")

        pl_table = self._cr.dictfetchall()

        return pl_table

    # Function to get revenue for MBK Group
    @api.model
    def get_revenue(self, division_id):
        self._cr.execute("""SELECT date FROM account_move WHERE state='posted' and company_id=3 order by date desc,id limit 1""")
        last_entry = self._cr.dictfetchall()
        if last_entry:
            last_entry_date = last_entry[0]['date']
        else:
            last_entry_date = date.today() + relativedelta(months=-1, day=1)

        analytic_id = int(division_id)
        month_from = last_entry_date.replace(day=1)
        month_to = month_from + relativedelta(months=+1, day=1, days=-1)
        last_to = month_from + relativedelta(days=-1)
        last_from = last_to.replace(day=1)
        year_from = date(month_to.year, 1, 1)
        year_to = date(month_to.year, 12, 31)
        s = "c"
        if s == "c":
            date_from = month_from
            date_to = month_to
        elif s == "l":
            date_from = last_from
            date_to = last_to
        else:
            date_from = year_from
            date_to = year_to

        self._cr.execute("""SELECT  AG.Name AS particulars, SUM(AML.credit-AML.debit) AS amount
                            FROM account_move_line AS AML 
                            INNER JOIN account_account A ON AML.account_id=A.id
                            INNER JOIN account_group AG ON A.group_id= AG.id
                            WHERE  AML.parent_state='posted' AND (AML.date BETWEEN '""" + str(date_from) + """' AND '""" + str(
            date_to) + """') AND AML.company_id=3 AND A.internal_group in ('income') AND (AML.analytic_account_id = '""" + str(
            analytic_id) + """' OR '""" + str(analytic_id) + """'=0) GROUP BY 1 ORDER BY 2 DESC""")

        income_table = self._cr.dictfetchall()

        return income_table

    # Function to get expense for MBK Group
    @api.model
    def get_expense(self, division_id):
        self._cr.execute("""SELECT date FROM account_move WHERE state='posted' and company_id=3 order by date desc,id limit 1""")
        last_entry = self._cr.dictfetchall()
        if last_entry:
            last_entry_date = last_entry[0]['date']
        else:
            last_entry_date = date.today() + relativedelta(months=-1, day=1)

        analytic_id = int(division_id)
        month_from = last_entry_date.replace(day=1)
        month_to = month_from + relativedelta(months=+1, day=1, days=-1)
        last_to = month_from + relativedelta(days=-1)
        last_from = last_to.replace(day=1)
        year_from = date(month_to.year, 1, 1)
        year_to = date(month_to.year, 12, 31)

        s = "c"

        if s == "c":
            date_from = month_from
            date_to = month_to
        elif s == "l":
            date_from = last_from
            date_to = last_to
        else:
            date_from = year_from
            date_to = year_to

        self._cr.execute("""SELECT  AG.Name AS particulars, SUM(AML.debit-AML.credit) AS amount
                            FROM account_move_line AS AML 
                            INNER JOIN account_account A ON AML.account_id=A.id
                            INNER JOIN account_group AG ON A.group_id= AG.id
                            WHERE  AML.parent_state='posted' AND (AML.date BETWEEN '""" + str(date_from) + """' AND '""" + str(
            date_to) + """') AND AML.company_id=3 AND A.internal_group in ('expense') AND (AML.analytic_account_id = '""" + str(
            analytic_id) + """' OR '""" + str(analytic_id) + """'=0) GROUP BY 1 ORDER BY 2 DESC""")

        expense_table = self._cr.dictfetchall()

        return expense_table

    # function to P&L chart
    @api.model
    def get_division_income_expense(self, division_id):
        self._cr.execute("""SELECT date FROM account_move WHERE state='posted' and company_id=3 order by date desc,id limit 1""")
        last_entry = self._cr.dictfetchall()
        if last_entry:
            last_entry_date = last_entry[0]['date']
        else:
            last_entry_date = date.today() + relativedelta(months=-1, day=1)

        analytic_id = int(division_id)
        month_from = last_entry_date.replace(day=1)
        month_to = month_from + relativedelta(months=+1, day=1, days=-1)
        last_to = month_from + relativedelta(days=-1)
        last_from = last_to.replace(day=1)
        year_from = date(month_to.year, 1, 1)
        year_to = date(month_to.year, 12, 31)

        if analytic_id == 0:
            self._cr.execute("""SELECT  AAA.code AS month, SUM(AML.credit-AML.debit) AS profit,                                                      
                                SUM(CASE WHEN A.internal_group='income' THEN AML.credit-AML.debit ELSE 0.00 END) AS income,                            
                                SUM(CASE WHEN A.internal_group='expense' THEN AML.debit-AML.credit ELSE 0.00 END) AS expense,
                                SUM(CASE WHEN A.user_type_id<>16 THEN AML.credit-AML.debit ELSE 0.00 END) AS opl
                                FROM account_move_line AS AML 
                                INNER JOIN account_account A ON AML.account_id=A.id
                                INNER JOIN account_group AG ON A.group_id= AG.id
                                INNER JOIN account_analytic_account AAA ON AML.analytic_account_id=AAA.id
                                WHERE AML.parent_state='posted' AND (AML.date BETWEEN '""" + str(month_from) + """' AND '""" + str(
                month_to) + """') AND AML.company_id=3 AND A.internal_group in ('income','expense') GROUP BY 1 ORDER BY 2 DESC""")
            pl_table = self._cr.dictfetchall()
        else:
            self._cr.execute("""SELECT TO_CHAR(AML.date, 'MON') AS month, SUM(AML.credit-AML.debit) AS profit,                                                      
                                SUM(CASE WHEN A.internal_group='income' THEN AML.credit-AML.debit ELSE 0.00 END) AS income,                            
                                SUM(CASE WHEN A.internal_group='expense' THEN AML.debit-AML.credit ELSE 0.00 END) AS expense,
                                SUM(CASE WHEN A.user_type_id<>16 THEN AML.credit-AML.debit ELSE 0.00 END) AS opl
                                FROM account_move_line AS AML 
                                INNER JOIN account_account A ON AML.account_id=A.id
                                INNER JOIN account_group AG ON A.group_id= AG.id
                                INNER JOIN account_analytic_account AAA ON AML.analytic_account_id=AAA.id
                                WHERE AML.parent_state='posted' AND (AML.date BETWEEN '""" + str(month_from) + """' AND '""" + str(
                month_to) + """') AND AML.company_id=3 AND A.internal_group in ('income','expense') AND (AML.analytic_account_id = '""" + str(analytic_id) + """')
                GROUP BY 1 ORDER BY 2 DESC""")
            pl_table = self._cr.dictfetchall()

        income = []
        expense = []
        month = []
        profit = []
        opl = []
        for rec in pl_table:
            month.append(rec['month'])
            income.append(round(rec['income'], 2))
            expense.append(round(rec['expense'], 2))
            opl.append(round(rec['opl'], 2))
            profit.append(round(rec['profit'], 2))
        return {
            'month': month,
            'income': income,
            'expense': expense,
            'opl': opl,
            'profit': profit
        }
