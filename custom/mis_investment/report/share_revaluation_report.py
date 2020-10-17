from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError

class FDSummaryReport(models.AbstractModel):
    _name = "report.mis_investment.report_share_revaluation_document"
    _description = "Revaluation Report"

    @api.model

    def get_total_qty(self,  productid, dtfilter):

        objstock = self.env['stock.valuation.layer'].search(
            [('product_id', '=', productid), ('create_date', '<=', dtfilter)])

        totqty=0.0
        for gr in objstock:
            totqty+=gr.quantity
        return totqty
    def get_closing_amount(self,  productid, dtfilter):

        objstock = self.env['stock.valuation.layer'].search(
            [('product_id', '=', productid), ('create_date', '<=', dtfilter)])

        closingamount=0.0
        for gr in objstock:
            closingamount+=gr.value
        return closingamount
        
    def get_last_closing_amount(self, reval_id, share_id, to_date ):
        objlastvalline = self.env['mis.invrevaluation.line'].search([('revaluation_id', '=', reval_id),  ('share_id', '=', share_id)])
        closingprice=0.0
        for valine in objlastvalline:
            closingprice=valine.closingprice
        return closingprice

    def get_last_unrelize_amount(self, reval_id, share_id, to_date ): 
        objlastvalline = self.env['mis.invrevaluation.line'].search([('revaluation_id', '=', reval_id),  ('share_id', '=', share_id)])
        unrelize_amount=0.0
        for valine in objlastvalline:
            unrelize_amount+=valine.unrealized_profit            
        return unrelize_amount

    def get_dividend(self, share_id, from_date, to_date):
        totaldivident=0.0
        objpro = self.env['product.product'].search([('investment_ok', '=', True), ('type', '=', 'product'),('id', '=', share_id)])
        
        analytictag = ""
        for tl in objpro.invest_analytic_tag_ids.ids:
            if analytictag != "":
                analytictag += ","
            analytictag += str(tl)
        strsql = """select COALESCE(sum(credit-debit),0.00) as dividend from 
                    account_move_line where parent_state='posted' and account_id in (select id from account_account where code in ('491102'))
                    and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
                    where account_analytic_tag_id in ("""+analytictag+""")) and date BETWEEN '""" + str(from_date) +"' AND '""" + str(to_date) +"'"""

        self._cr.execute(strsql)
        objdividend = self._cr.dictfetchall()
        for line in objdividend:
            totaldivident += line['dividend']
        return  totaldivident

    def get_brokerage_expense(self, share_id, from_date, to_date):
        brokerage_expense=0.0
        analytictag = ""
        objpro = self.env['product.product'].search([('investment_ok', '=', True), ('type', '=', 'product'),('id', '=', share_id)])
        
        for tl in objpro.invest_analytic_tag_ids.ids:
            if analytictag != "":
                analytictag += ","
            analytictag += str(tl)
        strsql = """select COALESCE(sum(debit-credit),0.00) as brokerage_expense from 
                    account_move_line where parent_state='posted' and account_id in (select id from account_account where code in ('491199'))
                    and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
                    where account_analytic_tag_id in ("""+analytictag+""")) and date BETWEEN '""" + str(from_date) +"' AND '""" + str(to_date) +"'"""

        self._cr.execute(strsql)

        objbrokerage = self._cr.dictfetchall()

        for line in objbrokerage:
            brokerage_expense+= line['brokerage_expense']
        return brokerage_expense



    def get_realized_profit_loss(self, share_id, from_date, to_date):
        totrealize_profit = 0.0 
        tot_amount = 0.00
        analytictag=""
        objpro = self.env['product.product'].search([('investment_ok', '=', True), ('type', '=', 'product'),('id', '=', share_id)])

        for tl in objpro.invest_analytic_tag_ids.ids:
            if analytictag!="":
                analytictag+=","
            analytictag+=str(tl)
        strsql ="""select COALESCE(sum(credit-debit),0.00) as totalprofit from 
        account_move_line where parent_state='posted' and account_id in (select id from account_account where code in ('491103','491104','491105'))
        and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
        where account_analytic_tag_id in ("""+analytictag+""")) and date BETWEEN '""" + str(from_date) +"' AND '""" + str(to_date) +"'"""

        self._cr.execute(strsql)
        objrealized_profit_loss = self._cr.dictfetchall()

        for line in objrealized_profit_loss:
            totrealize_profit += line['totalprofit']
        return totrealize_profit

    def _get_report_values(self, docids, data=None):

        from_date = data['date_from']
        to_date = data['date_to']
        dtfilter = to_date #+ timedelta(days=1)
        rptstatus=data['status']
        classification_id = data['classification']
        last_valudation_date=""

        reval_id=0
        master_table =[]

        objlastvaluation = self.env['mis.invrevaluation'].search([('trans_date', '<=', to_date),('state', '=', 'posted')], order='trans_date desc', limit=1)
        if objlastvaluation:
            tmpdate= objlastvaluation.trans_date
            last_valudation_date= tmpdate.strftime("%d-%m-%Y")
            reval_id=objlastvaluation.id
        if classification_id:
            objshare = self.env['product.product'].search([('investment_ok', '=', True), ('type', '=', 'product'), ('classification_id', '=', classification_id), ('categ_id', '=', 5)])
        else:
            objshare = self.env['product.product'].search([('investment_ok', '=', True), ('type', '=', 'product'), ('categ_id', '=', 5)])

        for shr in objshare:
            qty = self.get_total_qty(shr.id, dtfilter)
            closingprice = self.get_last_closing_amount(reval_id, shr.id, to_date)
            realize_profit = self.get_realized_profit_loss(shr.id, from_date, to_date)
            dividend = self.get_dividend(shr.id, from_date, to_date)
            brokerage_expense = self.get_brokerage_expense(shr.id,from_date, to_date)
            unrelize=self.get_last_unrelize_amount(reval_id, shr.id, to_date)
            closing_amount=self.get_closing_amount(shr.id, dtfilter)
            cost=0.00
            if qty>0.0:
                cost=closing_amount/qty
            
            
            if rptstatus=='All':
                if (qty!=0.0 or realize_profit!=0.0 or dividend!=0.0 or brokerage_expense!=0.0 or unrelize!=0.0):
                    master_table.append({
                        'sharerec': shr,
                        'qty': qty,
                        'cost': cost,
                        'closing_amount':closing_amount,
                        'closingprice': closingprice,
                        'realize_profit': realize_profit,
                        'dividend': dividend,
                        'brokerage_expense': brokerage_expense,
                        'unrelize' : unrelize,
                    })
            elif rptstatus=='Active':
                if (qty!=0.0):
                    master_table.append({
                        'sharerec': shr,
                        'qty': qty,
                        'cost': cost,
                        'closing_amount':closing_amount,
                        'closingprice': closingprice,
                        'realize_profit': realize_profit,
                        'dividend': dividend,
                        'brokerage_expense': brokerage_expense,
                        'unrelize' : unrelize,
                    })
            elif rptstatus=='Inactive':
                if (qty==0.0):
                    master_table.append({
                        'sharerec': shr,
                        'qty': qty,
                        'cost': cost,
                        'closing_amount':closing_amount,
                        'closingprice': closingprice,
                        'realize_profit': realize_profit,
                        'dividend': dividend,
                        'brokerage_expense': brokerage_expense,
                        'unrelize' : unrelize,
                    })                    

        #master_table.sort(key=lambda item:(item["closingprice"]*item["qty"]),reverse=True)
        sortedmaster_table= sorted(master_table, key=lambda item: (item["closingprice"]*item["qty"], item["realize_profit"]+item["unrelize"]+item["dividend"]-item["brokerage_expense"]), reverse=True)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'mis.invrevaluation',
            'docs': sortedmaster_table,
            'to_date': to_date,
            'header_date': data['header_date'],
            'lastdate': last_valudation_date,
        }
        return docargs