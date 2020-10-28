# -*- coding: utf-8 -*-

import calendar
import datetime
from datetime import datetime
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

from odoo import models, api
from odoo.http import request


class DashBoard(models.Model):
    _inherit = 'account.move'

    # function to getting late bills

    @api.model
    def get_latebills(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute(('''  select res_partner.name as partner, res_partner.commercial_partner_id as res  ,
                            account_move.commercial_partner_id as parent, sum(account_move.amount_total) as amount
                            from account_move,res_partner where 
                            account_move.partner_id=res_partner.id AND account_move.type = 'in_invoice' AND
                            invoice_payment_state = 'not_paid' AND 
                              account_move.company_id in (''' + str(company_ids) + ''') AND
                            state = 'posted'
                            AND  account_move.commercial_partner_id=res_partner.commercial_partner_id 
                            group by parent,partner,res
                            order by amount desc '''))

        record = self._cr.dictfetchall()

        bill_partner = [item['partner'] for item in record]

        bill_amount = [item['amount'] for item in record]

        amounts = sum(bill_amount[9:])
        name = bill_partner[9:]
        results = []
        pre_partner = []

        bill_amount = bill_amount[:9]
        bill_amount.append(amounts)
        bill_partner = bill_partner[:9]
        bill_partner.append("Others")
        records = {
            'bill_partner': bill_partner,
            'bill_amount': bill_amount,
            'result': results,

        }
        return records

        # return record

    # function to getting over dues

    @api.model
    def get_overdues(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute((''' select res_partner.name as partner, res_partner.commercial_partner_id as res  ,
                             account_move.commercial_partner_id as parent, sum(account_move.amount_total) as amount
                            from account_move, account_move_line ,res_partner where 
                            account_move.partner_id=res_partner.id AND account_move.type = 'out_invoice' AND
                            invoice_payment_state = 'not_paid' AND 
                            state = 'posted'
                            AND   account_move.company_id in (''' + str(company_ids) + ''') AND
			                 account_move_line.account_internal_type = 'payable' AND
                             account_move.commercial_partner_id=res_partner.commercial_partner_id 
                            group by parent,partner,res
                            order by amount desc
                            '''))

        record = self._cr.dictfetchall()
        due_partner = [item['partner'] for item in record]
        due_amount = [item['amount'] for item in record]

        amounts = sum(due_amount[9:])
        name = due_partner[9:]
        result = []
        pre_partner = []

        due_amount = due_amount[:9]
        due_amount.append(amounts)
        due_partner = due_partner[:9]
        due_partner.append("Others")
        records = {
            'due_partner': due_partner,
            'due_amount': due_amount,
            'result': result,

        }
        return records

    @api.model
    def get_overdues_this_month_and_year(self, *post):

        states_arg = ""
        if post[0] != 'posted':
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        company_ids = self.get_current_multi_company_value()
        if post[1] == 'this_month':
            self._cr.execute((''' 
                               select to_char(account_move.date, 'Month') as month, res_partner.name as due_partner, account_move.partner_id as parent,
                               sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                               AND account_move.type = 'out_invoice'
                               AND invoice_payment_state = 'not_paid'
                               AND state = 'posted' 
                               AND Extract(month FROM account_move.invoice_date_due) = Extract(month FROM DATE(NOW()))
                               AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                               AND account_move.partner_id = res_partner.commercial_partner_id
                               AND account_move.company_id in (''' + str(company_ids) + ''')
                               group by parent, due_partner, month
                               order by amount desc '''))
        else:
            self._cr.execute((''' select  res_partner.name as due_partner, account_move.partner_id as parent,
                                            sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                                            AND account_move.type = 'out_invoice'
                                            AND invoice_payment_state = 'not_paid'
                                            AND state = 'posted'
                                            AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.partner_id = res_partner.commercial_partner_id
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
    
                                            group by parent, due_partner
                                            order by amount desc '''))

        record = self._cr.dictfetchall()
        due_partner = [item['due_partner'] for item in record]
        due_amount = [item['amount'] for item in record]

        amounts = sum(due_amount[9:])
        name = due_partner[9:]
        result = []
        pre_partner = []

        due_amount = due_amount[:9]
        due_amount.append(amounts)
        due_partner = due_partner[:9]
        due_partner.append("Others")
        records = {
            'due_partner': due_partner,
            'due_amount': due_amount,
            'result': result,

        }
        return records

    @api.model
    def get_latebillss(self, *post):
        company_ids = self.get_current_multi_company_value()

        partners = self.env['res.partner'].search([('active', '=', True)])

        states_arg = ""
        if post[0] != 'posted':
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        if post[1] == 'this_month':
            self._cr.execute((''' 
                                select to_char(account_move.date, 'Month') as month, res_partner.name as bill_partner, account_move.partner_id as parent,
                                sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                                AND account_move.type = 'in_invoice'
                                AND invoice_payment_state = 'not_paid'
                                AND state = 'posted'
                                AND Extract(month FROM account_move.invoice_date_due) = Extract(month FROM DATE(NOW()))
                                AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                                AND account_move.company_id in (''' + str(company_ids) + ''')
                                AND account_move.partner_id = res_partner.commercial_partner_id
                                group by parent, bill_partner, month
                                order by amount desc '''))
        else:
            self._cr.execute((''' select res_partner.name as bill_partner, account_move.partner_id as parent,
                                            sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                                            AND account_move.type = 'in_invoice'
                                            AND invoice_payment_state = 'not_paid'
                                            AND state = 'posted'
                                            AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.partner_id = res_partner.commercial_partner_id
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
                                            group by parent, bill_partner
                                            order by amount desc '''))

        result = self._cr.dictfetchall()
        bill_partner = [item['bill_partner'] for item in result]

        bill_amount = [item['amount'] for item in result]

        amounts = sum(bill_amount[9:])
        name = bill_partner[9:]
        results = []
        pre_partner = []

        bill_amount = bill_amount[:9]
        bill_amount.append(amounts)
        bill_partner = bill_partner[:9]
        bill_partner.append("Others")
        records = {
            'bill_partner': bill_partner,
            'bill_amount': bill_amount,
            'result': results,

        }
        return records

    # function to get total invoice

    @api.model
    def get_total_invoice(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute(('''select sum(amount_total) as customer_invoice from account_move where type ='out_invoice'
                            AND  state = 'posted' AND account_move.company_id in (''' + str(company_ids) + ''')           
                        ''') )
        record_customer = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total) as supplier_invoice from account_move where type ='in_invoice' 
                          AND  state = 'posted'  AND account_move.company_id in (''' + str(company_ids) + ''')      
                        '''))
        record_supplier = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total) as credit_note from account_move where type ='out_refund'
                          AND  state = 'posted' AND account_move.company_id in (''' + str(company_ids) + ''')      
                        '''))
        result_credit_note = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total) as refund from account_move where type ='in_refund'
                          AND  state = 'posted' AND account_move.company_id in (''' + str(company_ids) + ''')   
                        ''') )
        result_refund = self._cr.dictfetchall()

        customer_invoice = [item['customer_invoice'] for item in record_customer]
        supplier_invoice = [item['supplier_invoice'] for item in record_supplier]
        credit_note = [item['credit_note'] for item in result_credit_note]
        refund = [item['refund'] for item in result_refund]

        return customer_invoice, credit_note, supplier_invoice, refund

    @api.model
    def get_total_invoice_current_year(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute(('''select sum(amount_total_signed) as customer_invoice from account_move where type ='out_invoice'
                            AND state = 'posted'                               
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                            AND account_move.company_id in (''' + str(company_ids) + ''')           
                        '''))
        record_customer_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) as supplier_invoice from account_move where type ='in_invoice'
                            AND state = 'posted'                             
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                            AND account_move.company_id in (''' + str(company_ids) + ''')    
                        '''))
        record_supplier_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed)) as credit_note from account_move where type ='out_refund'
                            AND  state = 'posted'                               
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                            AND account_move.company_id in (''' + str(company_ids) + ''')      
                        '''))
        result_credit_note_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) as refund from account_move where type ='in_refund'
                            AND state = 'posted'                              
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                            AND account_move.company_id in (''' + str(company_ids) + ''')   
                        '''))
        result_refund_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total_signed) - sum(amount_residual_signed)  as customer_invoice_paid from account_move where type ='out_invoice'
                                    AND  state = 'posted'
                                    AND invoice_payment_state = 'paid'
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                    AND account_move.company_id in (''' + str(company_ids) + ''')
                                '''))
        record_paid_customer_invoice_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed))  as supplier_invoice_paid from account_move where type ='in_invoice'
                                    AND  state = 'posted'
                                    AND  invoice_payment_state = 'paid'
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                    AND account_move.company_id in (''' + str(company_ids) + ''')
                                '''))
        result_paid_supplier_invoice_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed))  as customer_credit_paid from account_move where type ='out_refund'
                                            AND state = 'posted'
                                            AND invoice_payment_state = 'paid'
                                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
                                        '''))
        record_paid_customer_credit_current_year = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total_signed) - sum(amount_residual_signed)  as supplier_refund_paid from account_move where type ='in_refund'
                                            AND state = 'posted'
                                            AND  invoice_payment_state = 'paid'
                                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
                                        '''))
        result_paid_supplier_refund_current_year = self._cr.dictfetchall()

        customer_invoice_current_year = [item['customer_invoice'] for item in record_customer_current_year]
        supplier_invoice_current_year = [item['supplier_invoice'] for item in record_supplier_current_year]

        credit_note_current_year = [item['credit_note'] for item in result_credit_note_current_year]
        refund_current_year = [item['refund'] for item in result_refund_current_year]

        paid_customer_invoice_current_year = [item['customer_invoice_paid'] for item in
                                              record_paid_customer_invoice_current_year]
        paid_supplier_invoice_current_year = [item['supplier_invoice_paid'] for item in
                                              result_paid_supplier_invoice_current_year]

        paid_customer_credit_current_year = [item['customer_credit_paid'] for item in
                                             record_paid_customer_credit_current_year]
        paid_supplier_refund_current_year = [item['supplier_refund_paid'] for item in
                                             result_paid_supplier_refund_current_year]

        return customer_invoice_current_year, credit_note_current_year, supplier_invoice_current_year, refund_current_year, paid_customer_invoice_current_year, paid_supplier_invoice_current_year, paid_customer_credit_current_year, paid_supplier_refund_current_year

    @api.model
    def get_total_invoice_current_month(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute(('''select sum(amount_total_signed) as customer_invoice from account_move where type ='out_invoice'
                                    AND state = 'posted'                             
                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                                    AND account_move.company_id in (''' + str(company_ids) + ''')           
                                '''))
        record_customer_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) as supplier_invoice from account_move where type ='in_invoice'
                                    AND state = 'posted'                             
                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                                    AND account_move.company_id in (''' + str(company_ids) + ''')      
                                '''))
        record_supplier_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed)) as credit_note from account_move where type ='out_refund'
                                    AND  state = 'posted'                              
                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                                    AND account_move.company_id in (''' + str(company_ids) + ''')      
                                '''))
        result_credit_note_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) as refund from account_move where type ='in_refund'
                                    AND state = 'posted'                               
                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))     
                                    AND account_move.company_id in (''' + str(company_ids) + ''')   
                                '''))
        result_refund_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total_signed) - sum(amount_residual_signed)  as customer_invoice_paid from account_move where type ='out_invoice'
                                            AND state = 'posted'
                                            AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
                                        '''))
        record_paid_customer_invoice_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed))  as supplier_invoice_paid from account_move where type ='in_invoice'
                                            AND  state = 'posted'
                                            AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                            AND account_move.company_id in (''' + str(company_ids) + ''')
                                        '''))
        result_paid_supplier_invoice_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(-(amount_total_signed)) - sum(-(amount_residual_signed))  as customer_credit_paid from account_move where type ='out_refund'
                                                    AND state = 'posted'
                                                    AND invoice_payment_state = 'paid'
                                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                                    AND account_move.company_id in (''' + str(company_ids) + ''')
                                                '''))
        record_paid_customer_credit_current_month = self._cr.dictfetchall()

        self._cr.execute(('''select sum(amount_total_signed) - sum(amount_residual_signed)  as supplier_refund_paid from account_move where type ='in_refund'
                                                    AND state = 'posted'
                                                    AND  invoice_payment_state = 'paid'
                                                    AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))
                                                    AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))
                                                    AND account_move.company_id in (''' + str(company_ids) + ''')
                                                '''))
        result_paid_supplier_refund_current_month = self._cr.dictfetchall()

        customer_invoice_current_month = [item['customer_invoice'] for item in record_customer_current_month]
        supplier_invoice_current_month = [item['supplier_invoice'] for item in record_supplier_current_month]
        credit_note_current_month = [item['credit_note'] for item in result_credit_note_current_month]
        refund_current_month = [item['refund'] for item in result_refund_current_month]
        paid_customer_invoice_current_month = [item['customer_invoice_paid'] for item in
                                               record_paid_customer_invoice_current_month]
        paid_supplier_invoice_current_month = [item['supplier_invoice_paid'] for item in
                                               result_paid_supplier_invoice_current_month]

        paid_customer_credit_current_month = [item['customer_credit_paid'] for item in
                                              record_paid_customer_credit_current_month]
        paid_supplier_refund_current_month = [item['supplier_refund_paid'] for item in
                                              result_paid_supplier_refund_current_month]

        currency = self.get_currency()
        return customer_invoice_current_month, credit_note_current_month, supplier_invoice_current_month, refund_current_month, paid_customer_invoice_current_month, paid_supplier_invoice_current_month, paid_customer_credit_current_month, paid_supplier_refund_current_month, currency

    @api.model
    def get_total_invoice_this_month(self, *post):

        company_ids = self.get_current_multi_company_value()

        states_arg = ""
        if post != ('posted',):
            states_arg = """ state in ('posted', 'draft')"""
        else:
            states_arg = """ state = 'posted'"""

        self._cr.execute(('''select sum(amount_total) from account_move where type = 'out_invoice' 
                            AND state = 'posted'
                            AND Extract(month FROM account_move.date) = Extract(month FROM DATE(NOW()))      
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW()))   
                            AND account_move.company_id in (''' + str(company_ids) + ''')
                            '''))
        record = self._cr.dictfetchall()
        return record

    # function to get total invoice last month

    @api.model
    def get_total_invoice_last_month(self):

        one_month_ago = (datetime.now() - relativedelta(months=1)).month

        self._cr.execute('''select sum(amount_total) from account_move where type = 'out_invoice' AND
                               account_move.state = 'posted'
                            AND Extract(month FROM account_move.date) = ''' + str(one_month_ago) + ''' 
                            ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total invoice last year

    @api.model
    def get_total_invoice_last_year(self):

        self._cr.execute(''' select sum(amount_total) from account_move where type = 'out_invoice' 
                            AND account_move.state = 'posted'
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW())) - 1    
                                ''')
        record = self._cr.dictfetchall()
        return record

    # function to get total invoice this year

    @api.model
    def get_total_invoice_this_year(self):

        company_ids = self.get_current_multi_company_value()

        self._cr.execute(''' select sum(amount_total) from account_move where type = 'out_invoice'
                            AND Extract(YEAR FROM account_move.date) = Extract(YEAR FROM DATE(NOW())) AND
                               account_move.state = 'posted'   AND
                                account_move.company_ids in (''' + str(company_ids) + ''')
                                    ''')
        record = self._cr.dictfetchall()
        return record

    @api.model
    def get_current_company_value(self):
        current_company = request.httprequest.cookies.get('cids')
        if current_company:
            company_id = int(current_company[0])
        else:
            company_id = self.env.company.id
        if company_id not in self.env.user.company_ids.ids:
            company_id = self.env.company.id
        return company_id

    def get_current_multi_company_value(self):
        current_company = request.httprequest.cookies.get('cids')
        if current_company:
            company_ids = int(current_company[0])
        else:
            company_ids = self.env.company.id
        if company_ids not in self.env.user.company_ids.ids:
            company_ids = self.env.company.id
        return company_ids

    @api.model
    def get_currency(self):
        current_company = self.env['res.company'].browse(self.get_current_company_value())
        default = current_company.currency_id or self.env.ref('base.main_company').currency_id
        lang = self.env.user.lang
        if not lang:
            lang = 'en_US'
        lang = lang.replace("_", '-')
        currency = {'position': default.position, 'symbol': default.symbol, 'language': lang}
        return currency
