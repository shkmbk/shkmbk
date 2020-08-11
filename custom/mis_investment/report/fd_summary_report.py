from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError

class FDSummaryReport(models.AbstractModel):
    _name = "report.mis_investment.report_fd_summary_document"
    _description = "Fixed Deposit Summary"

    @api.model
    def _get_report_values(self, docids, data=None):
        to_date = data['date_to']
        type_id = data['type']


        if type_id:
            fixeddeposit_ids = self.env['product.product'].search([('investment_ok', '=', True), ('isdeposit', '=', True), ('maturity_date', '>=', to_date), ('type_id', '=', type_id)],order='maturity_date')
        else:
            fixeddeposit_ids = self.env['product.product'].search([('investment_ok', '=', True), ('isdeposit', '=', True), ('maturity_date', '>=', to_date)],order='maturity_date')

        self._cr.execute("""select id, (maturity_date::date - deposit_date::date)+1 as totaldays, 
        ('""" + str(to_date) + """'::date-deposit_date::date)+1 as totalason,expected_earning
        from product_template where investment_ok=true and maturity_date>='"""+str(to_date)+"""'
        and isdeposit = true""")
        objrec = self._cr.dictfetchall()
        subtable = {}
        for line in objrec:
            if line['totaldays']>0:
                subtable[line['id']] = (line['expected_earning']*(line['totalason']/line['totaldays']))
            else:
                subtable[line['id']]=0

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'mis.invrevaluation',
            'docs': fixeddeposit_ids,
            'to_date': to_date,
            'subtable': subtable,
        }
        return docargs