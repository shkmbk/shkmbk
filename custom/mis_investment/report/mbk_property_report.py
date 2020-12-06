from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


class PropertySummaryReport(models.AbstractModel):
    _name = "report.mis_investment.report_mbk_property_document"
    _description = "Property Summary Report"

    def _get_report_values(self, docids, data=None):
        from_date = data['date_from']
        to_date = data['date_to']
        year = int(data['year'])
        month = int(data['month'])
        year_from = date(year, month, 1)
        year_to = year_from + relativedelta(months=+1, day=1, days=-1)
        obj_re = self.env['mbk.property'].search(
            [('state', '=', 'posted'), ('date_to', '>=', year_from), ('date_to', '<=', year_to)],
            order='date_to', limit=1)
        if not obj_re:
            raise UserError('No records found in selected parameter')

        self._cr.execute("""SELECT AAA.id,AAA.name AS Building, SUM(REL.occupied_nos) AS occupied_nos,SUM(REL.non_renewal) AS non_renewal, SUM(REL.booked_nos) AS booked_nos, SUM(REL.vacant_nos) AS vacant_nos, SUM(REL.total_nos) AS total_nos,
                                SUM(REL.occupied_nos)*100/NULLIF(SUM(REL.total_nos),0) AS occupancy_rate
                                FROM mbk_property RE 
                                INNER JOIN mbk_property_line REL ON RE.id=REL.property_id
                                INNER JOIN account_analytic_account AAA ON AAA.id=REL.analytic_account_id
                            WHERE RE.state='posted' AND RE.company_id=3 AND (RE.date_to BETWEEN '"""+str(year_from)+"""' AND '"""+str(year_to)+"""') 
                            GROUP BY AAA.name,AAA.id
                            ORDER BY occupancy_rate,occupied_nos""")
        master_table = self._cr.dictfetchall()

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'mbk.property',
            'docs': master_table,
            'header_period': data['header_period'],
            'from_date': year_from.strftime("%d/%m/%Y"),
            'to_date': year_to.strftime("%d/%m/%Y"),
        }
        return docargs
