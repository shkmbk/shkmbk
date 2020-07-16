from odoo import models, fields, api, _
from datetime import date
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError

class MisInvestmentRevaluation(models.Model):
    _name = 'mis.invrevaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description ='Share Valuation'

    state = fields.Selection([
        ('draft', 'New'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    name = fields.Char('Name')
    ref = fields.Char('Referenec', required=True)
    trans_date = fields.Date('Date')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)
    trans_line = fields.One2many('mis.invrevaluation.line', 'revaluation_id', string='Revaluation Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    move_id= fields.Many2one('account.move', 'Posted Journal')

    def get_total_qty(self,  productid):
        dtfilter = self.trans_date + timedelta(days=1)
        objstock = self.env['stock.valuation.layer'].search(
            [('product_id', '=', productid), ('create_date', '<', dtfilter)])

        totqty=0.0
        for gr in objstock:
            totqty+=gr.quantity
        return totqty

    def check_unrealized_profit_a_c(self, shareid):
        analytictag=""
        for tl in shareid.invest_analytic_tag_ids.ids:
            if analytictag!="":
                analytictag+=","
            analytictag+=str(tl)
        strsql="""select COALESCE(sum(debit-credit),0.00) as unrealized_profit_a_c from 
        account_move_line where account_id in (select id from account_account where code in ('491101'))
        and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
        where account_analytic_tag_id in ("""+analytictag+""")) and date<='""" + str(self.trans_date) +"'"""" 
         and parent_state='posted' and company_id="""+ str(self.company_id.id)
        #raise UserError(strsql)

        self._cr.execute(strsql)
        objrealized_profit_loss = self._cr.dictfetchall()

        amount =0.0
        for line in objrealized_profit_loss:
            amount += line['unrealized_profit_a_c']
        return amount

    def calculate_brokerage_expense(self, shareid):
        for rec in self:
            analytictag = ""
            for tl in shareid.invest_analytic_tag_ids.ids:
                if analytictag != "":
                    analytictag += ","
                analytictag += str(tl)
            strsql="""select COALESCE(sum(debit-credit),0.00) as brokerage_expense from 
                         account_move_line where account_id in (select id from account_account where code in ('491199'))
                         and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
                         where  account_analytic_tag_id in (""" + analytictag + """)) and date<='""" + str(
                self.trans_date) + "'"" and parent_state='posted' and company_id="""+ str(self.company_id.id)
            #raise UserError(strsql)
            self._cr.execute(strsql)
            objbrokerage = self._cr.dictfetchall()
            amount = 0.0
            for line in objbrokerage:
                amount += line['brokerage_expense']
            return amount


    def calculate_dividend(self, shareid):
        for rec in self:
            analytictag = ""
            for tl in shareid.invest_analytic_tag_ids.ids:
                if analytictag != "":
                    analytictag += ","
                analytictag += str(tl)
            strsql="""select COALESCE(sum(credit-debit),0.00) as dividend from 
                         account_move_line where account_id in (select id from account_account where code in ('491102'))
                         and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
                         where  account_analytic_tag_id in (""" + analytictag + """)) and date<='""" + str(
                self.trans_date) + "'"" and parent_state='posted' and company_id="""+ str(self.company_id.id)

            #raise UserError(strsql)
            self._cr.execute(strsql)
            objdividend = self._cr.dictfetchall()
            amount = 0.0
            for line in objdividend:
                amount += line['dividend']
            return amount

    def calculate_realized_profit_loss(self, shareid):
        for rec in self:
            tot_amount = 0.00
            analytictag = ""
            for tl in shareid.invest_analytic_tag_ids.ids:
                if analytictag != "":
                    analytictag += ","
                analytictag += str(tl)
                strsql = """select COALESCE(sum(credit-debit),0.00) as totalprofit from 
                account_move_line where account_id in (select id from account_account where code in ('491103','491104','491105'))
                and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
                where account_analytic_tag_id in (""" + analytictag + """)) and date<='""" + str(
                    self.trans_date) + "'"" and parent_state='posted' and company_id="""+ str(self.company_id.id)

            #            raise UserError(strsql)
            self._cr.execute(strsql)
            objrealized_profit_loss = self._cr.dictfetchall()
            amount=0.0
            for line in objrealized_profit_loss:
                amount += line['totalprofit']
        return amount


    def action_loaddetail(self):
        if len(self.trans_line)==0:
            objpro = self.env['product.product'].search([('investment_ok', '=', True), ('type', '=', 'product')])
            new_lines = self.env['mis.invrevaluation.line']
            for rec in objpro:
                totqty=self.get_total_qty(rec.id)
                unrealized_profit_a_c = self.check_unrealized_profit_a_c(rec)
                brokerage_expense = self.calculate_brokerage_expense(rec)
                dividend = self.calculate_dividend(rec)
                realized_profit_loss= self.calculate_realized_profit_loss(rec)
                if totqty>0 or unrealized_profit_a_c!=0.0:
                    create_vals = {'revaluation_id': self.id,
                                   'share_id': rec.id,
                                   'share_qty': totqty,
                                   'closingprice': 0.00,
                                   'closing_amount': 0.00,
                                   'unrealized_profit_a_c': unrealized_profit_a_c,
                                   'realized_profit_loss': realized_profit_loss,
                                   'brokerage_expense': brokerage_expense,
                                   'dividend': dividend,
                                   }
                    new_lines.create(create_vals)
            return new_lines

    def button_posted(self):
        isheader =False
        totalamt =0.00
        objinvestment = self.env['account.analytic.account'].search([('name', '=', 'Investment')])
        obj123202 = self.env['account.account'].search([('code', '=', '123202')])
        obj491101 = self.env['account.account'].search([('code', '=', '491101')])
        move_line_vals = []

        journal_id =0
        for rec in self.trans_line:
            totalamt+=rec.unrealized_profit_a_c
            journal_id = rec.share_id.categ_id.property_stock_journal.id
            isheader = True

        #journal_id = self.share_id.categ_id.property_stock_journal.id

        for rec in self.trans_line:
            journalamount=(rec.unrealized_profit_a_c-(-1*rec.unrealized_profit))
            if journalamount< 0:
                create_vals =  (0,0,{'name': self.ref,
                               'date': self.trans_date,
                               'ref': 'Share Revalution Posting  ' + str(self.trans_date),
                               'parent_state': 'draft',
                               'company_id': self.company_id.id,
                               'account_id': obj491101.id,
                               'quantity': 1,
                               'analytic_account_id': objinvestment.id,
                               'analytic_tag_ids': rec.share_id.invest_analytic_tag_ids.ids,
                               'debit': -1*journalamount,
                               'credit': 0.0,
                               })
                move_line_vals.append(create_vals)

                create_vals =  (0,0,{'name': self.ref,
                               'date': self.trans_date,
                               'ref': 'Share Revalution Posting ' + str(self.trans_date),
                               'parent_state': 'draft',
                               'company_id': self.company_id.id,
                               'account_id': obj123202.id,
                               'quantity': 1,
                               'analytic_account_id': objinvestment.id,
                               'analytic_tag_ids': rec.share_id.invest_analytic_tag_ids.ids,
                               'credit': -1*journalamount,
                               'debit': 0.0,
                               })
                move_line_vals.append(create_vals)

            if journalamount>0:
                create_vals =  (0,0,{'date': self.trans_date,
                               'name': self.ref,
                               'ref': 'Share Revalution Posting ' + str(self.trans_date),
                               'parent_state': 'draft',
                               'company_id': self.company_id.id,
                               'analytic_account_id': objinvestment.id,
                               'account_id': obj491101.id,
                               'quantity': 1,
                               'analytic_tag_ids': rec.share_id.invest_analytic_tag_ids.ids,
                               'credit': journalamount,
                               'debit': 0.0,
                               })
                move_line_vals.append(create_vals)

                create_vals =  (0,0,{
                               'date': self.trans_date,
                               'name': self.ref,
                               'ref': 'Share Revalution Posting ' + str(self.trans_date),
                               'parent_state': 'draft',
                               'company_id': self.company_id.id,
                               'analytic_account_id': objinvestment.id,
                               'account_id': obj123202.id,
                               'quantity': 1,
                               'analytic_tag_ids': rec.share_id.invest_analytic_tag_ids.ids,
                               'debit': journalamount,
                               'credit': 0.0,
                               })
                move_line_vals.append(create_vals)

        if isheader == True:
            move_vals  = {'date': self.trans_date,
                            'journal_id': journal_id,
                            'ref': 'Share Revalution Posting ' + str(self.trans_date),
                            'name': '/',
                            'company_id': self.company_id.id,
                            'state': 'draft',
                            'type': 'entry',
                            'amount_total': totalamt,
                            'line_ids': move_line_vals,
                            }
            objacmove=self.env['account.move'].create(move_vals)
        objacmove.post()
        self.move_id=objacmove.id

        self.state='posted'
        if self.name=='Draft':
            self.name=self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code('mis.invrevaluation') or _('New')


    def button_cancel(self):
        self.state='cancel'

    def button_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        vals['state'] = 'draft'
        vals['name'] = 'Draft'
        #        if vals.get('name', _('New')) == _('New'):
#            if 'company_id' in vals:
#                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
#                    'mis.invrevaluation') or _('New')
#            else:
#                vals['name'] = self.env['ir.sequence'].next_by_code('mis.invrevaluation') or _('New')
        result = super(MisInvestmentRevaluation, self).create(vals)
        return result
        
    def unlink(self):
        for invest in self:
            if invest.name != 'Draft' and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been posted."))
            invest.trans_line.unlink()
        return super(MisInvestmentRevaluation, self).unlink()

class MisInvestmentRevaluationLine(models.Model):
    _name = 'mis.invrevaluation.line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Share Monthly profit and loss transaction Line'


    revaluation_id = fields.Many2one('mis.invrevaluation', string='Revaluation Reference', index=True, required=True,
                               ondelete='cascade')
    share_id = fields.Many2one('product.product', string='Share', domain=[('investment_ok', '=', True), ('isdeposit', '=', True)], change_default=True)
    share_qty = fields.Float(string='Quantity',  required=True)
    closingprice = fields.Float(string='Closing Price', required=True)
    closing_amount = fields.Float(string='Closing Amount', compute='calculate_amount', store=True)
    unrealized_profit = fields.Float(string='Unrealize Profit / Loss', compute='calculate_amount', store=True)
    cost = fields.Float(string='Cost', compute='calculate_cost', store=True)
    amount = fields.Float(string='Amount', compute='calculate_cost', store=True)

    realized_profit_loss = fields.Float(string='Realize Profit / Loss', readonly=True, store=True)

    dividend = fields.Float(string='Dividend', readonly=True,
                                        store=True)
    brokerage_expense = fields.Float(string='Brokerage & Other Expense', readonly=True,
                                        store=True)
    net_profit_loss = fields.Float(string='Net Profit / Loss', compute='calculate_realized_profit_loss',
                                        store=True)
    unrealized_profit_a_c = fields.Float(string='Unrealize Profit / Loss A/C', sreadonly=True, store=True)




    @api.depends('share_id')
    def calculate_cost(self):
        for rec in self:

            dtfilter = self.revaluation_id.trans_date + timedelta(days=1)
            objcost = self.env['stock.valuation.layer'].search([('product_id', '=', rec.share_id.id), ('create_date', '<=', dtfilter)])
            fltotalcost=0.00
            fltotalqty =0.00
            for ocost in objcost:
               fltotalqty+=ocost.quantity
               fltotalcost += ocost.value

            if fltotalqty!=0:
                rec.cost = fltotalcost/fltotalqty
                rec.amount = fltotalcost

    @api.depends('closingprice')
    def calculate_amount(self):
        for rec in self:
            tot_amount =0.00
            rec.closing_amount = rec.share_qty*rec.closingprice
            rec.unrealized_profit=rec.closing_amount- rec.amount
            rec.net_profit_loss = ((rec.unrealized_profit+rec.realized_profit_loss+rec.dividend)-rec.brokerage_expense)
