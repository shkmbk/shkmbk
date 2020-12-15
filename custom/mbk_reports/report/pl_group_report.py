from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from pytz import timezone
from dateutil.relativedelta import relativedelta
import pytz


class PLGroup_Report(models.AbstractModel):
    _name = 'report.mbk_reports.report_pl_group'
    _description = "MBK Profit and Loss Report"

    def _get_report_values(self, docids, data=None):
        year = int(data['year'])
        month = int(data['month'])
        is_detailed = data['is_detailed']
        month_from = date(year, month, 1)
        month_to = month_from + relativedelta(months=+1, day=1, days=-1)
        year_from = date(year, 1, 1)
        year_to = date(year, 12, 31)
        last_to = month_from + relativedelta(days=-1)
        last_from = last_to.replace(day=1)
        analytic_id = 0
        if analytic_id:
            analytic_id_c = analytic_id
        else:
            analytic_id_c = 0

        self._cr.execute("""SELECT AG.Name AS particulars,
                            SUM(AML.credit-AML.debit) AS total,
                            SUM(CASE WHEN AML.analytic_account_id=9 THEN AML.credit-AML.debit ELSE 0.00 END) AS ADWV,
                            SUM(CASE WHEN AML.analytic_account_id=10 THEN AML.credit-AML.debit ELSE 0.00 END) AS ADPM,
                            SUM(CASE WHEN AML.analytic_account_id=11 THEN AML.credit-AML.debit ELSE 0.00 END) AS MBKS,
                            SUM(CASE WHEN AML.analytic_account_id=12 THEN AML.credit-AML.debit ELSE 0.00 END) AS RMAD,
                            SUM(CASE WHEN AML.analytic_account_id=13 THEN AML.credit-AML.debit ELSE 0.00 END) AS RMFJ,
                            SUM(CASE WHEN AML.analytic_account_id=14 THEN AML.credit-AML.debit ELSE 0.00 END) AS UTAB,
                            SUM(CASE WHEN AML.analytic_account_id=15 THEN AML.credit-AML.debit ELSE 0.00 END) AS UTFJ,
                            SUM(CASE WHEN AML.analytic_account_id=16 THEN AML.credit-AML.debit ELSE 0.00 END) AS FJML,
                            SUM(CASE WHEN AML.analytic_account_id=17 THEN AML.credit-AML.debit ELSE 0.00 END) AS GLXC,
                            SUM(CASE WHEN AML.analytic_account_id=18 THEN AML.credit-AML.debit ELSE 0.00 END) AS SHCT,
                            SUM(CASE WHEN AML.analytic_account_id=19 THEN AML.credit-AML.debit ELSE 0.00 END) AS MBKM                                                        
                            FROM account_move_line AS AML 
                            INNER JOIN account_account A ON AML.account_id=A.id
                            INNER JOIN account_group AG ON A.group_id= AG.id
                            WHERE  AML.parent_state='posted' AND (AML.date BETWEEN '"""+str(month_from)+"""' AND '"""+str(month_to)+"""') AND AML.company_id=3 AND A.internal_group in ('income')
                            GROUP BY AG.Name ORDER BY 2 DESC""")

        income_table = self._cr.dictfetchall()

        self._cr.execute("""SELECT AG.Name AS particulars,
                            SUM(AML.debit-AML.credit) AS total,
                            SUM(CASE WHEN AML.analytic_account_id=9 THEN AML.debit-AML.credit ELSE 0.00 END) AS ADWV,
                            SUM(CASE WHEN AML.analytic_account_id=10 THEN AML.debit-AML.credit ELSE 0.00 END) AS ADPM,
                            SUM(CASE WHEN AML.analytic_account_id=11 THEN AML.debit-AML.credit ELSE 0.00 END) AS MBKS,
                            SUM(CASE WHEN AML.analytic_account_id=12 THEN AML.debit-AML.credit ELSE 0.00 END) AS RMAD,
                            SUM(CASE WHEN AML.analytic_account_id=13 THEN AML.debit-AML.credit ELSE 0.00 END) AS RMFJ,
                            SUM(CASE WHEN AML.analytic_account_id=14 THEN AML.debit-AML.credit ELSE 0.00 END) AS UTAB,
                            SUM(CASE WHEN AML.analytic_account_id=15 THEN AML.debit-AML.credit ELSE 0.00 END) AS UTFJ,
                            SUM(CASE WHEN AML.analytic_account_id=16 THEN AML.debit-AML.credit ELSE 0.00 END) AS FJML,
                            SUM(CASE WHEN AML.analytic_account_id=17 THEN AML.debit-AML.credit ELSE 0.00 END) AS GLXC,
                            SUM(CASE WHEN AML.analytic_account_id=18 THEN AML.debit-AML.credit ELSE 0.00 END) AS SHCT,
                            SUM(CASE WHEN AML.analytic_account_id=19 THEN AML.debit-AML.credit ELSE 0.00 END) AS MBKM                         
                            FROM account_move_line AS AML 
                            INNER JOIN account_account A ON AML.account_id=A.id
                            INNER JOIN account_group AG ON A.group_id= AG.id
                            WHERE  AML.parent_state='posted' AND (AML.date BETWEEN '"""+str(month_from)+"""' AND '"""+str(month_to)+"""') AND AML.company_id=3 AND A.internal_group in ('expense') and A.user_type_id<>16
                            GROUP BY AG.Name ORDER BY 2 DESC""")

        expense_table = self._cr.dictfetchall()

        self._cr.execute("""SELECT 'Depreciation and Amortization' AS particulars,
                            SUM(AML.debit-AML.credit) AS total,
                            SUM(CASE WHEN AML.analytic_account_id=9 THEN AML.debit-AML.credit ELSE 0.00 END) AS ADWV,
                            SUM(CASE WHEN AML.analytic_account_id=10 THEN AML.debit-AML.credit ELSE 0.00 END) AS ADPM,
                            SUM(CASE WHEN AML.analytic_account_id=11 THEN AML.debit-AML.credit ELSE 0.00 END) AS MBKS,
                            SUM(CASE WHEN AML.analytic_account_id=12 THEN AML.debit-AML.credit ELSE 0.00 END) AS RMAD,
                            SUM(CASE WHEN AML.analytic_account_id=13 THEN AML.debit-AML.credit ELSE 0.00 END) AS RMFJ,
                            SUM(CASE WHEN AML.analytic_account_id=14 THEN AML.debit-AML.credit ELSE 0.00 END) AS UTAB,
                            SUM(CASE WHEN AML.analytic_account_id=15 THEN AML.debit-AML.credit ELSE 0.00 END) AS UTFJ,
                            SUM(CASE WHEN AML.analytic_account_id=16 THEN AML.debit-AML.credit ELSE 0.00 END) AS FJML,
                            SUM(CASE WHEN AML.analytic_account_id=17 THEN AML.debit-AML.credit ELSE 0.00 END) AS GLXC,
                            SUM(CASE WHEN AML.analytic_account_id=18 THEN AML.debit-AML.credit ELSE 0.00 END) AS SHCT,
                            SUM(CASE WHEN AML.analytic_account_id=19 THEN AML.debit-AML.credit ELSE 0.00 END) AS MBKM                             
                            FROM account_move_line AS AML 
                            INNER JOIN account_account A ON AML.account_id=A.id
                            INNER JOIN account_group AG ON A.group_id= AG.id
                            WHERE  AML.parent_state='posted' AND (AML.date BETWEEN '"""+str(month_from)+"""' AND '"""+str(month_to)+"""') AND AML.company_id=3 AND A.internal_group in ('expense') and A.user_type_id=16 ORDER BY 2 DESC""")

        dep_table = self._cr.dictfetchall()

        income_total = 0.00
        adwv_income = 0.00
        adpm_income = 0.00
        mbks_income = 0.00
        rmad_income = 0.00
        rmfj_income = 0.00
        utab_income = 0.00
        utfj_income = 0.00
        fjml_income = 0.00
        glxc_income = 0.00
        shct_income = 0.00
        mbkm_income = 0.00
        expense_total = 0.00
        adwv_expense = 0.00
        adpm_expense = 0.00
        mbks_expense = 0.00
        rmad_expense = 0.00
        rmfj_expense = 0.00
        utab_expense = 0.00
        utfj_expense = 0.00
        fjml_expense = 0.00
        glxc_expense = 0.00
        shct_expense = 0.00
        mbkm_expense = 0.00
        dep_total = 0.00
        adwv_dep = 0.00
        adpm_dep = 0.00
        mbks_dep = 0.00
        rmad_dep = 0.00
        rmfj_dep = 0.00
        utab_dep = 0.00
        utfj_dep = 0.00
        fjml_dep = 0.00
        glxc_dep = 0.00
        shct_dep = 0.00
        mbkm_dep = 0.00
        opl_total = 0.00
        adwv_opl = 0.00
        adpm_opl = 0.00
        mbks_opl = 0.00
        rmad_opl = 0.00
        rmfj_opl = 0.00
        utab_opl = 0.00
        utfj_opl = 0.00
        fjml_opl = 0.00
        glxc_opl = 0.00
        shct_opl = 0.00
        mbkm_opl = 0.00

        master_table = []

        # Opening Balance

        for rec in income_table:
            income_total += rec['total']
            adwv_income += rec['adwv']
            adpm_income += rec['adpm']
            mbks_income += rec['mbks']
            rmad_income += rec['rmad']
            rmfj_income += rec['rmfj']
            utab_income += rec['utab']
            utfj_income += rec['utfj']
            fjml_income += rec['fjml']
            glxc_income += rec['glxc']
            shct_income += rec['shct']
            mbkm_income += rec['mbkm']

        for rec in expense_table:
            expense_total += rec['total']
            adwv_expense += rec['adwv']
            adpm_expense += rec['adpm']
            mbks_expense += rec['mbks']
            rmad_expense += rec['rmad']
            rmfj_expense += rec['rmfj']
            utab_expense += rec['utab']
            utfj_expense += rec['utfj']
            fjml_expense += rec['fjml']
            glxc_expense += rec['glxc']
            shct_expense += rec['shct']
            mbkm_expense += rec['mbkm']

        for rec in dep_table:
            if rec['total']:
                dep_total += rec['total']
                adwv_dep += rec['adwv']
                adpm_dep += rec['adpm']
                mbks_dep += rec['mbks']
                rmad_dep += rec['rmad']
                rmfj_dep += rec['rmfj']
                utab_dep += rec['utab']
                utfj_dep += rec['utfj']
                fjml_dep += rec['fjml']
                glxc_dep += rec['glxc']
                shct_dep += rec['shct']
                mbkm_dep += rec['mbkm']

        opl_total = income_total - expense_total
        adwv_opl = adwv_income - adwv_expense
        adpm_opl = adpm_income - adpm_expense
        mbks_opl = mbks_income - mbks_expense
        rmad_opl = rmad_income - rmad_expense
        rmfj_opl = rmfj_income - rmfj_expense
        utab_opl = utab_income - utab_expense
        utfj_opl = utfj_income - utfj_expense
        fjml_opl = fjml_income - fjml_expense
        glxc_opl = glxc_income - glxc_expense
        shct_opl = shct_income - shct_expense
        mbkm_opl = mbkm_income - mbkm_expense

        particulars_0 = 'REVENUE'
        particulars_1 = 'EXPENDITURE'
        particulars_2 = 'Net Operating Income / Loss'
        particulars_3 = 'Depreciation and Amortization'
        particulars_4 = 'Net Profit / Loss'

        master_table.append({
            'particulars': particulars_0,
            'total': income_total,
            'adwv': adwv_income,
            'adpm': adpm_income,
            'mbks': mbks_income,
            'rmad': rmad_income,
            'rmfj': rmfj_income,
            'utab': utab_income,
            'utfj': utfj_income,
            'fjml': fjml_income,
            'glxc': glxc_income,
            'shct': shct_income,
            'mbkm': mbkm_income,
        })
        master_table.append({
            'particulars': particulars_1,
            'total': expense_total,
            'adwv': adwv_expense,
            'adpm': adpm_expense,
            'mbks': mbks_expense,
            'rmad': rmad_expense,
            'rmfj': rmfj_expense,
            'utab': utab_expense,
            'utfj': utfj_expense,
            'fjml': fjml_expense,
            'glxc': glxc_expense,
            'shct': shct_expense,
            'mbkm': mbkm_expense,
        })
        master_table.append({
            'particulars': particulars_2,
            'total': opl_total,
            'adwv': adwv_opl,
            'adpm': adpm_opl,
            'mbks': mbks_opl,
            'rmad': rmad_opl,
            'rmfj': rmfj_opl,
            'utab': utab_opl,
            'utfj': utfj_opl,
            'fjml': fjml_opl,
            'glxc': glxc_opl,
            'shct': shct_opl,
            'mbkm': mbkm_opl,
        })
        master_table.append({
            'particulars': particulars_3,
            'total': dep_total,
            'adwv': adwv_dep,
            'adpm': adpm_dep,
            'mbks': mbks_dep,
            'rmad': rmad_dep,
            'rmfj': rmfj_dep,
            'utab': utab_dep,
            'utfj': utfj_dep,
            'fjml': fjml_dep,
            'glxc': glxc_dep,
            'shct': shct_dep,
            'mbkm': mbkm_dep,
        })
        master_table.append({
            'particulars': particulars_4,
            'total': opl_total - dep_total,
            'adwv': adwv_opl - adwv_dep,
            'adpm': adpm_opl - adpm_dep,
            'mbks': mbks_opl - mbks_dep,
            'rmad': rmad_opl - rmad_dep,
            'rmfj': rmfj_opl - rmfj_dep,
            'utab': utab_opl - utab_dep,
            'utfj': utfj_opl - utfj_dep,
            'fjml': fjml_opl - fjml_dep,
            'glxc': glxc_opl - glxc_dep,
            'shct': shct_opl - shct_dep,
            'mbkm': mbkm_opl - mbkm_dep,
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
        }
        return docargs
