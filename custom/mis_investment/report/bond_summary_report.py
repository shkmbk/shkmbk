from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError

class BondSummaryReport(models.AbstractModel):
    _name = "report.mis_investment.report_bond_summary_document"
    _description = "Bond Summary"

    @api.model
    def _get_report_values(self, docids, data=None):
        s_to_date = data['date_to']
        type_id = data['type']
        inv_currency_id = data['currency']
        header_date=data['header_date']

        to_date= datetime.strptime(s_to_date , '%Y-%m-%d').date()
        
        cur = self.env['res.currency'].search([('id', '=', inv_currency_id)], limit=1)
        currency= cur.name

        if type_id:
            bond_ids = self.env['product.product'].search([('investment_ok', '=', True), ('isdeposit', '=', True), ('maturity_date', '>', to_date), ('type_id', '=', type_id), ('categ_id', '=', 18)],order='maturity_date')
        else:
            bond_ids = self.env['product.product'].search([('investment_ok', '=', True), ('isdeposit', '=', True), ('maturity_date', '>', to_date), ('categ_id', '=', 18)],order='maturity_date')
        master_table =[]

        if not bond_ids:
            raise UserError('There are no stock found for selected parameters')

        for bd in bond_ids:
            b_earningasof=0.00
            b_amount=0.00
            cur_rate=0.00
            b_expected_earning=0.00

            cur_rate=bd.inv_currency_rate
            b_amount=bd.list_price*cur_rate
            b_expected_earning= bd.expected_earning*cur_rate
            b_earningasof= (bd.expected_earning *((to_date-bd.deposit_date).days+1))/(bd.maturity_date-bd.deposit_date).days

            master_table.append({
                'bond': bd.name,
                'deposit_date': bd.deposit_date.strftime("%d-%m-%Y"),
                'maturity_date': bd.maturity_date.strftime("%d-%m-%Y"),
                'list_price':b_amount,
                'interest_rate': bd.interest_rate,
                'expected_earning': b_expected_earning,
                'earningasof': b_earningasof,
            })

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'mis.invrevaluation',
            'docs':master_table,
            'to_date': header_date,
            'currency': currency,
        }
        return docargs