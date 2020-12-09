from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class FEReport(models.AbstractModel):
    _name = "report.mbk_reports.report_fe"
    _description = "Family Expense Report"

    def _get_report_values(self, docids, data=None):
        s_from_date = data['from_date']
        s_to_date = data['to_date']
        analytic_id = data['analytic_id']

        if not analytic_id:
            analytic_id = 0

        from_date = datetime.strptime(s_from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(s_to_date , '%Y-%m-%d').date()

        obj_aml = self.env['account.move.line'].search(
            [('parent_state', '=', 'posted'), ('date', '>=', from_date), ('date', '<=', to_date)],
            order='date', limit=1)
        if not obj_aml:
            raise UserError('No records found in selected parameter')

        self._cr.execute("""SELECT T.name AS particulars,NULL AS mn, NULL AS account,
            NULL AS description,
            SUM(debit-credit) AS amount,
            NULL dt, 0 AS order_id, NULL AS id,T.id AS tag_id FROM
            account_move_line AML INNER JOIN account_account A ON AML.account_id=A.id
            INNER JOIN account_analytic_tag_account_move_line_rel AAT ON AML.id=AAT.account_move_line_id
            INNER JOIN account_analytic_tag T ON AAT.account_analytic_tag_id=T.id
            WHERE AML.parent_state='posted' AND T.analytic_tag_group=42 AND internal_group IN('expense', 'equity') 
            AND A.code<>'999998' AND (AML.date BETWEEN '"""+str(from_date)+"""' AND '"""+str(to_date)+"""') AND (T.id = '"""+str(analytic_id)+"""' OR '"""+str(analytic_id)+"""'=0)            
            GROUP BY T.name,T.id
            UNION ALL
            SELECT NULL AS particulars, to_char(AML.date, 'Mon YYYY') AS mn, A.name AS account,
            AML.name AS description,
            debit-credit AS amount,            
            AML.date AS dt, 1 AS order_id, AML.id, T.id AS tag_id FROM
            account_move_line AML INNER JOIN account_account A ON AML.account_id=A.id
            INNER JOIN account_analytic_tag_account_move_line_rel AAT ON AML.id=AAT.account_move_line_id
            INNER JOIN account_analytic_tag T ON AAT.account_analytic_tag_id=T.id
            WHERE AML.parent_state='posted' AND T.analytic_tag_group=42 AND internal_group IN('expense', 'equity') AND A.code<>'999998'
            AND (AML.date BETWEEN '"""+str(from_date)+"""' AND '"""+str(to_date)+"""') AND (T.id = '"""+str(analytic_id)+"""' OR '"""+str(analytic_id)+"""'=0)
            ORDER BY tag_id,order_id,dt""")

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
