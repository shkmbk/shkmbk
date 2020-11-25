from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError

class MCBondRevaluationReport(models.AbstractModel):
    _name = "report.mis_investment.report_mc_bond_summary_document"
    _description = "Multi-Currency Bond Summary Report"

    def _get_report_values(self, docids, data=None):

        from_date = data['date_from']
        to_date = data['date_to']
        dt_filter = to_date
        rpt_status = data['status']
        classification_id = data['classification']
        inv_currency_id = data['currency']

        c_rate = self.env['res.currency'].search([('id', '=', inv_currency_id)], limit=1).rate
        c_name = self.env['res.currency'].search([('id', '=', inv_currency_id)], limit=1).name

        master_table =[]

        if classification_id:
            objbond = self.env['product.product'].search([('investment_ok', '=', True), ('type', '=', 'product'), ('inv_currency_id', '=', inv_currency_id), ('classification_id', '=', classification_id), ('categ_id', '=', 19)])
        else:
            objbond = self.env['product.product'].search([('investment_ok', '=', True), ('type', '=', 'product'), ('inv_currency_id', '=', inv_currency_id), ('categ_id', '=', 19)])

        for shr in objbond:
            obj_stock = self.env['stock.valuation.layer'].search([('product_id', '=', shr.id), ('create_date', '<=', dt_filter)])
            c_rate = shr.inv_currency_rate
            c_name = shr.inv_currency_id.name
            cur_rate = round((1 / c_rate), 4)
            qty = 0.0
            closing_amount = 0.00
            realize_profit = 0.00
            income = 0.00
            expense = 0.00
            for gr in obj_stock:
                qty += gr.quantity
                closing_amount += gr.value
            journal_items = self.env['account.move.line'].search(
                [('analytic_tag_ids', 'in', shr.invest_analytic_tag_ids.ids), ('parent_state', '=', 'posted'),
                 ('account_id.internal_group', 'in', ['expense', 'income'])])
            for line in journal_items:
                if line.account_id in [shr.categ_id.property_account_income_categ_id.id, shr.categ_id.property_stock_account_output_categ_id.id]:
                    realize_profit += line.credit - line.debit
                elif line.account_id.internal_group == 'income':
                    income += line.credit - line.debit
                else:
                    expense += line.debit-line.credit

            net_profit_loss = realize_profit + income - expense
            cost = 0.00
            if qty > 0.0:
                cost = (closing_amount/qty)
            cost = cost * c_rate
            closing_amount = closing_amount * c_rate
            realize_profit = realize_profit * c_rate
            income = income * c_rate
            expense = expense * c_rate
            net_profit_loss = net_profit_loss * c_rate

            if rpt_status == 'All':
                if (qty != 0.0 or realize_profit != 0.0 or income != 0.0 or expense != 0.0):
                    master_table.append({
                        'bond_rec': shr,
                        'qty': qty,
                        'cost': cost,
                        'closing_amount': closing_amount,
                        'realize_profit': realize_profit,
                        'income': income,
                        'expense': expense,
                        'net_profit_loss': net_profit_loss,
                    })
            elif rpt_status == 'Active':
                if (qty != 0.0):
                    master_table.append({
                        'bond_rec': shr,
                        'qty': qty,
                        'cost': cost,
                        'closing_amount': closing_amount,
                        'realize_profit': realize_profit,
                        'income': income,
                        'expense': expense,
                        'net_profit_loss': net_profit_loss,
                    })
            elif rpt_status == 'Inactive':
                if (qty == 0.0):
                    master_table.append({
                        'bond_rec': shr,
                        'qty': qty,
                        'cost': cost,
                        'closing_amount': closing_amount,
                        'realize_profit': realize_profit,
                        'income': income,
                        'expense': expense,
                        'net_profit_loss': net_profit_loss,
                    })                    

        sortedmaster_table = sorted(master_table, key=lambda item: (item["closing_amount"], item["net_profit_loss"]), reverse=True)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'mis.invrevaluation',
            'docs': sortedmaster_table,
            'to_date': to_date,
            'header_date': data['header_date'],
            'c_name': c_name,
        }
        return docargs