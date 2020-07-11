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
    trans_date = fields.Date('Date')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)
    trans_line = fields.One2many('mis.invrevaluation.line', 'revaluation_id', string='Revaluation Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)

    def get_total_qty(self,  productid):
        dtfilter = self.trans_date + timedelta(days=1)
        objstock = self.env['stock.valuation.layer'].search(
            [('product_id', '=', productid), ('create_date', '<', dtfilter)])

        totqty=0.0
        for gr in objstock:
            totqty+=gr.quantity
        return totqty


    def action_loaddetail(self):
        if len(self.trans_line)==0:
            objpro = self.env['product.product'].search([('investment_ok', '=', True), ('type', '=', 'product')])
            new_lines = self.env['mis.invrevaluation.line']
            for rec in objpro:
                totqty=self.get_total_qty(rec.id)
                if totqty>0:
                    create_vals = {'revaluation_id': self.id,
                                   'share_id': rec.id,
                                   'share_qty': totqty,
                                   'closingprice': 0.00,
                                   'closing_amount': 0.00,
                                   'unrealized_profit': 0.00,
                                   }
                    new_lines.create(create_vals)
            return new_lines

    def button_posted(self):

        isheader =False
        totalamt =0.00
        objacmove = self.env['account.move']
        objacmoveline = self.env['account.move.line']
        objinvestment = self.env['account.analytic.account'].search([('name', '=', 'Investment')])
        obj123202 = self.env['account.account'].search([('code', '=', '123202')])
        obj491101 = self.env['account.account'].search([('code', '=', '491101')])


        for rec in self.trans_line:
            totalamt+=rec.unrealized_profit_a_c


        for rec in self.trans_line:
            if isheader==False:
                journal_id= rec.share_id.categ_id.property_stock_journal
                isheader = True
                create_hvals = {'date': self.trans_date,
                                'journal_id': journal_id.id,
                                'ref': 'Share Revalution Posting ' + str(self.trans_date),
                                'company_id': self.env.company.id,
                                'state': 'draft',
                                'type': 'entry',
                                'amount_total_signed': totalamt,
                                'amount_total': totalamt,
                               }
                mvheader = objacmove.create(create_hvals)

            if self.trans_line.unrealized_profit_a_c< 0:
                create_vals = {'move_id': mvheader.id,
                               'date': self.trans_date,
                               'ref': 'Share Revalution Posting  ' + str(self.trans_date),
                               'parent_state': 'draft',
                               'company_id': self.env.company.id,
                               'account_id': obj491101.id,
                               'account_analytic_id': objinvestment.id,
                               'analytic_tags_ids': self.trans_line.share_id.invest_analytic_tag_ids,
                               'debit': self.trans_line.unrealized_profit_a_c,
                               }
                objacmoveline.create(create_vals)
                create_vals = {'move_id': mvheader.id,
                               'date': self.trans_date,
                               'ref': 'Stock Revalution Auto Post on ' + str(self.trans_date),
                               'parent_state': 'draft',
                               'company_id': self.env.company.id,
                               'account_id': obj123202.id,
                               'account_analytic_id': objinvestment.id,
                               'analytic_tags_ids': self.trans_line.share_id.invest_analytic_tag_ids,
                               'credit': self.trans_line.unrealized_profit_a_c,
                               }
                objacmoveline.create(create_vals)

            if self.trans_line.unrealized_profit_a_c>0:
                create_vals = {'move_id': mvheader.id,
                               'date': self.trans_date,
                               'ref': 'Stock Revalution Auto Post ' + str(self.trans_date),
                               'parent_state': 'draft',
                               'company_id': self.env.company.id,
                               'account_analytic_id': objinvestment.id,
                               'account_id': obj123202.id,
                               'analytic_tags_ids': self.trans_line.share_id.invest_analytic_tag_ids,
                               'credit': self.trans_line.unrealized_profit_a_c,
                               }
                objacmoveline.create(create_vals)
                create_vals = {'move_id': mvheader.id,
                               'date': self.trans_date,
                               'ref': 'Stock Revalution Auto Post ' + str(self.trans_date),
                               'parent_state': 'draft',
                               'company_id': self.env.company.id,
                               'account_analytic_id': objinvestment.id,
                               'account_id': obj491101.id,
                               'analytic_tags_ids': self.trans_line.share_id.invest_analytic_tag_ids,
                               'debit': self.trans_line.unrealized_profit_a_c,
                               }
                objacmoveline.create(create_vals)
            #objacmove.post()
        self.state='posted'


    def button_cancel(self):
        self.state='cancel'

    def button_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        vals['state'] = 'draft'
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'mis.invrevaluation') or _('New')
            # vals['state'] = self.jobcard_status
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('mis.invrevaluation') or _('New')
        result = super(MisInvestmentRevaluation, self).create(vals)
        return result

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
    amount = fields.Float(string='Amount', compute='calculate_amount', store=True)

    realized_profit_loss = fields.Float(string='Realize Profit / Loss', compute='calculate_realized_profit_loss', store=True)

    dividend = fields.Float(string='Dividend', compute='calculate_dividend',
                                        store=True)
    brokerage_expense = fields.Float(string='Brokerage & Other Expense', compute='calculate_brokerage_expense',
                                        store=True)
    net_profit_loss = fields.Float(string='Net Profit / Loss', compute='calculate_realized_profit_loss',
                                        store=True)
    unrealized_profit_a_c = fields.Float(string='Unrealize Profit / Loss A/C', compute='calculate_unrealized_profit_a_c', store=True)

    @api.depends('closingprice')
    def calculate_brokerage_expense(self):
        for rec in self:
            analytictag = ""
            for tl in self.share_id.invest_analytic_tag_ids.ids:
                if analytictag != "":
                    analytictag += ","
                analytictag += str(tl)
            # raise UserError(analytictag)
            self._cr.execute("""select COALESCE(sum(debit-credit),0.00) as brokerage_expense from 
                        account_move_line where account_id in (select id from account_account where code in ('491199'))
                        and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
                        where  account_analytic_tag_id in ("""+analytictag+""")) and date='""" + str(self.revaluation_id.trans_date) +"'""")
            objbrokerage = self._cr.dictfetchall()

            for line in objbrokerage:
                rec.brokerage_expense = line['brokerage_expense']


    @api.depends('closingprice')
    def calculate_dividend(self):
        for rec in self:
            analytictag = ""
            for tl in self.share_id.invest_analytic_tag_ids.ids:
                if analytictag != "":
                    analytictag += ","
                analytictag += str(tl)
            # raise UserError(analytictag)
            self._cr.execute("""select COALESCE(sum(credit-debit),0.00) as dividend from 
                        account_move_line where account_id in (select id from account_account where code in ('491102'))
                        and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
                        where  account_analytic_tag_id in ("""+analytictag+""")) and date='""" + str(self.revaluation_id.trans_date) +"'""")
            objdividend = self._cr.dictfetchall()
            for line in objdividend:
                rec.dividend = line['dividend']

    @api.depends('share_id')
    def calculate_cost(self):
        for rec in self:
           #objproduct = self.env['ir.property'].search([('name', '=', 'standard_price'), ('res_id', '=', 'product.product,'+str(rec.share_id.id))])
           # for pro in objproduct:
           #     rec.cost=pro.value_float
            dtfilter = self.revaluation_id.trans_date + timedelta(days=1)
            objcost = self.env['stock.valuation.layer'].search([('product_id', '=', rec.share_id.id), ('create_date', '<=', dtfilter)])
            fltotalcost=0.00
            fltotalqty =0.00
            for ocost in objcost:
               fltotalqty+=ocost.quantity
               fltotalcost += ocost.value
            if fltotalqty!=0:
                rec.cost = fltotalcost/fltotalqty

    @api.depends('closingprice')
    def calculate_amount(self):
        for rec in self:
            tot_amount =0.00
            rec.closing_amount = rec.share_qty*rec.closingprice
            rec.unrealized_profit=rec.closing_amount- rec.amount
            rec.net_profit_loss = ((rec.unrealized_profit+rec.realized_profit_loss+rec.dividend)-rec.brokerage_expense)

    @api.depends('share_id')
    def calculate_unrealized_profit_a_c(self):
        for rec in self:
            tot_amount = 0.00
            analytictag=""
            for tl in self.share_id.invest_analytic_tag_ids.ids:
                if analytictag!="":
                    analytictag+=","
                analytictag+=str(tl)
            #raise UserError(analytictag)
            self._cr.execute("""select COALESCE(sum(debit-credit),0.00) as unrealized_profit_a_c from 
            account_move_line where account_id in (select id from account_account where code in ('491101'))
            and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
            where account_analytic_tag_id in ("""+analytictag+""")) and date='""" + str(self.revaluation_id.trans_date) +"'""")
            objrealized_profit_loss = self._cr.dictfetchall()
            for line in objrealized_profit_loss:
                rec.unrealized_profit_a_c = line['unrealized_profit_a_c']


    @api.depends('share_id')
    def calculate_realized_profit_loss(self):
        for rec in self:
            tot_amount = 0.00
            analytictag=""
            for tl in self.share_id.invest_analytic_tag_ids.ids:
                if analytictag!="":
                    analytictag+=","
                analytictag+=str(tl)
                strsql ="""select COALESCE(sum(credit-debit),0.00) as totalprofit from 
            account_move_line where account_id in (select id from account_account where code in ('491103','491104','491105'))
            and id in (select account_move_line_id from account_analytic_tag_account_move_line_rel 
            where account_analytic_tag_id in ("""+analytictag+""")) and date='""" + str(self.revaluation_id.trans_date) +"'"""

            #raise UserError(strsql)
            self._cr.execute(strsql)
            objrealized_profit_loss = self._cr.dictfetchall()

            for line in objrealized_profit_loss:
                rec.realized_profit_loss = line['totalprofit']

