from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class FESummaryReport(models.AbstractModel):
    _name = "report.mbk_reports.report_fe_summary"
    _description = "Family Expense Summary Report"

    def _get_report_values(self, docids, data=None):
        s_from_date = data['from_date']
        s_to_date = data['to_date']

        from_date= datetime.strptime(s_from_date, '%Y-%m-%d').date()
        to_date= datetime.strptime(s_to_date , '%Y-%m-%d').date()

        obj_aml = self.env['account.move.line'].search(
            [('parent_state', '=', 'posted'), ('date', '>=', from_date), ('date', '<=', to_date)],
            order='date', limit=1)
        if not obj_aml:
            raise UserError('No records found in selected parameter')

        self._cr.execute("""SELECT to_char(AML.date, 'Mon YYYY') AS particulars, NULL AS account,
            SUM(debit-credit) AS total,
            SUM(CASE WHEN T.Name ='SHK SULTAN' THEN debit-credit ELSE 0.00 END) AS shk_sultan,
            SUM(CASE WHEN T.Name ='SHK ZAYED' THEN  debit-credit ELSE 0.00 END) AS shk_zayed,
            SUM(CASE WHEN T.Name ='SHK HAMDAN' THEN  debit-credit ELSE 0.00 END) AS shk_hamdan,
            SUM(CASE WHEN T.Name ='HER HIGHNESS' THEN  debit-credit ELSE 0.00 END) AS her_highness,
            SUM(CASE WHEN T.Name ='HH' THEN  debit-credit ELSE 0.00 END) AS his_highness,
            to_char(AML.date, 'YYYYMM') AS mid, 0 AS order_id FROM
            account_move_line AML INNER JOIN account_account A ON AML.account_id=A.id
            INNER JOIN account_analytic_tag_account_move_line_rel AAT ON AML.id=AAT.account_move_line_id
            INNER JOIN account_analytic_tag T ON AAT.account_analytic_tag_id=T.id
            WHERE AML.parent_state='posted' AND T.analytic_tag_group=42 AND internal_group IN('expense', 'equity') AND A.code<>'999998' AND (AML.date BETWEEN '"""+str(from_date)+"""' AND '"""+str(to_date)+"""')
            GROUP BY Particulars, mid
            UNION ALL
            SELECT NULL AS particulars, A.name AS account,
            SUM(debit-credit) AS total,
            SUM(CASE WHEN T.Name ='SHK SULTAN' THEN debit-credit ELSE 0.00 END) AS shk_sultan,
            SUM(CASE WHEN T.Name ='SHK ZAYED' THEN  debit-credit ELSE 0.00 END) AS shk_zayed,
            SUM(CASE WHEN T.Name ='SHK HAMDAN' THEN  debit-credit ELSE 0.00 END) AS shk_hamdan,
            SUM(CASE WHEN T.Name ='HER HIGHNESS' THEN  debit-credit ELSE 0.00 END) AS her_highness,
            SUM(CASE WHEN T.Name ='HH' THEN  debit-credit ELSE 0.00 END) AS his_highness,
            to_char(AML.date, 'YYYYMM') AS mid, 1 AS order_id FROM
            account_move_line AML INNER JOIN account_account A ON AML.account_id=A.id
            INNER JOIN account_analytic_tag_account_move_line_rel AAT ON AML.id=AAT.account_move_line_id
            INNER JOIN account_analytic_tag T ON AAT.account_analytic_tag_id=T.id
            WHERE AML.parent_state='posted' AND T.analytic_tag_group=42 AND internal_group IN('expense', 'equity') AND A.code<>'999998' AND (AML.date BETWEEN '"""+str(from_date)+"""' AND '"""+str(to_date)+"""')
            GROUP BY A.name,particulars,mid
            ORDER BY mid,order_id""")

        master_table = self._cr.dictfetchall()

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'account.move.line',
            'docs': master_table,
            'header_period': data['header_period'],
            'from_date': from_date.strftime("%d/%m/%Y"),
            'to_date': to_date.strftime("%d/%m/%Y"),
        }
        return docargs
