from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError

class FDSummaryReport(models.AbstractModel):
    _name = "report.mis_investment.report_share_revaluation_document"
    _description = "Revaluation Report"

    @api.model

    def get_total_qty(self,  productid, dtfilter):

        objstock = self.env['stock.valuation.layer'].search(
            [('product_id', '=', productid), ('create_date', '<', dtfilter)])

        totqty=0.0
        for gr in objstock:
            totqty+=gr.quantity
        return totqty
    def get_last_closing_amount(self, reval_id, share_id, to_date ):
        objlastvalline = self.env['mis.invrevaluation.line'].search([('revaluation_id', '=', reval_id),  ('share_id', '=', share_id)])
        closeamt=0.0
        for valine in objlastvalline:
            closeamt=valine.closingprice
        return closeamt

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

        self._cr.execute("""select COALESCE(sum(credit-debit),0.00) as dividend from 
                    account_move_line where account_id in (select id from account_account where code in ('491102'))
                    and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
                    where  account_analytic_tag_id in ("""+analytictag+""")) and date BETWEEN '""" + str(from_date) +"'""" +"""AND '""" + str(to_date) +"'""")
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
        # raise UserError(analytictag)
        self._cr.execute("""select COALESCE(sum(debit-credit),0.00) as brokerage_expense from 
                    account_move_line where account_id in (select id from account_account where code in ('491199'))
                    and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
                    where  account_analytic_tag_id in ("""+analytictag+""")) and date BETWEEN '""" + str(from_date) +"'""" +"""AND '""" + str(to_date) +"'""")
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
                analytictag+=",";
            analytictag+=str(tl)
        strsql ="""select COALESCE(sum(credit-debit),0.00) as totalprofit from 
        account_move_line where account_id in (select id from account_account where code in ('491103','491104','491105'))
        and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
        where account_analytic_tag_id in ("""+analytictag+""")) and date BETWEEN '""" + str(from_date) +"'""" +"""AND '""" + str(to_date) +"'"""
        self._cr.execute(strsql)
        objrealized_profit_loss = self._cr.dictfetchall()

        for line in objrealized_profit_loss:
            totrealize_profit += line['totalprofit']
        return totrealize_profit




    def _get_report_values(self, docids, data=None):

        from_date = data['date_from']
        to_date = data['date_to']
        dtfilter = to_date #+ timedelta(days=1)
        last_valudation_date=""
        table4expearn = {}
        table4qty = {}
        table4closingamt = {}
        table4realize_profit={}
        table4dividend = {}
        table4brokerage_expense={}
        table4unrelize={}
        table4lastvaluation = {}
        reval_id=0

        objlastvaluation = self.env['mis.invrevaluation'].search([('trans_date', '<=' ,to_date)], order='trans_date desc', limit=1)
        if objlastvaluation:
            last_valudation_date= objlastvaluation.trans_date
            reval_id=objlastvaluation.id

        objshare = self.env['product.product'].search([('investment_ok', '=', True), ('type', '=', 'product')])
        for shr in objshare:
            table4qty[shr.id] = self.get_total_qty(shr.id, dtfilter)
            table4closingamt[shr.id] = self.get_last_closing_amount(reval_id, shr.id, to_date)
            table4realize_profit[shr.id] = self.get_realized_profit_loss(shr.id, from_date, to_date)
            table4dividend[shr.id] = self.get_dividend(shr.id, from_date, to_date)
            table4brokerage_expense[shr.id] = self.get_brokerage_expense(shr.id,from_date, to_date)
            table4unrelize[shr.id]=self.get_last_unrelize_amount(reval_id, shr.id, to_date)        

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'mis.invrevaluation',
            'docs': objshare,
            'to_date': to_date,
            'subtable': table4expearn,
            'lastdate': last_valudation_date,
            'table4qty':table4qty,
            'table4closingamt': table4closingamt,
            'table4realize_profit': table4realize_profit,
            'table4dividend': table4dividend,
            'table4brokerage_expense': table4brokerage_expense,
            'table4unrelize': table4unrelize,
        }
        return docargs