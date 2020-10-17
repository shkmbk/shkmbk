from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError, UserError


class MisProduct(models.Model):
    _inherit = 'product.template'

    def _suminvestexpense(self):
        objJournal = self.env['account.move.line'].search(
            [('analytic_tag_ids', 'in', self.invest_analytic_tag_ids.ids), ('parent_state', '=', 'posted'), ('account_id.internal_group', 'in', ['expense', 'income'])])
        sum = 0.00
        for jor in objJournal:
            sum += (jor.credit-jor.debit)
        self.sum_invest_expense = sum

    investment_ok = fields.Boolean(string="Can be Investment", track_visibility='onchange')
    isdeposit = fields.Boolean(string="Is Deposit?", track_visibility='onchange')
    deposit_date = fields.Date(string="Deposit Date", track_visibility='onchange')
    maturity_date = fields.Date(string="Maturity date", track_visibility='onchange')
    classification_id = fields.Many2one('mis.inv.classfication', string="Classification")
    risk_id = fields.Many2one('mis.inv.riskrate', string="Risk")
    liquidityreturn_id = fields.Many2one('mis.inv.liquidityreturn', string="Liquidity Return")
    geographic_id = fields.Many2one('mis.inv.geographic', string="Geographic")
    responsibility_id = fields.Many2one('res.partner', string="Responsibility")
    invest_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    sum_invest_expense = fields.Float(string="P&L", compute='_suminvestexpense')
    bank_journal = fields.Many2one('account.journal', string="Bank Account", domain=" [('type', '=', 'bank')]")
    interest_rate = fields.Float(string="Interest Rate")
    day_in_a_year = fields.Integer(string="No of Days in Year")
    expected_earning = fields.Float(string="Expected Earning", compute='calculate_interest', store=True, default=False)
    type_id = fields.Many2one('mis.inv.type', string="Type")
    inv_currency_id = fields.Many2one('res.currency', string="Currency")
    inv_currency_rate = fields.Float(default='1.00', string="Exchange Rate", digits=(12, 12))

    @api.depends('interest_rate', 'day_in_a_year', 'deposit_date', 'maturity_date')
    def calculate_interest(self):
        for rec in self:
            tot_expect_earning = 0.00
            if rec.interest_rate > 0 and rec.day_in_a_year > 0:
                if rec.deposit_date and rec.maturity_date and rec.isdeposit == True:
                    totdays = (rec.maturity_date - rec.deposit_date).days
                    tot_expect_earning = rec.list_price * (rec.interest_rate / (rec.day_in_a_year * 100)) * totdays
                    rec.expected_earning = round(tot_expect_earning, 2)

    def action_fd_expiry_notification(self):
        for rec in self:
            display_msg = rec.categ_id.name + """ """ + rec.name + """ will mature on """ + rec.maturity_date.strftime(
                "%d-%m-%Y") + """,
                           <br/>
                           Principal Amount: """ + str(rec.list_price) + """<br/>
                           Deposit Date: """ + rec.deposit_date.strftime("%d-%m-%Y") + """<br/>
                           Interest Rate: """ + str(rec.interest_rate) + """%<br/>
                           Interest Amount: """ + str(round(rec.expected_earning, 2)) + """<br/>
                           Interest Rate: """ + str(rec.interest_rate)
            rec.message_post(body=display_msg, partner_ids=[3, 368], author_id=2, message_type='notification',
                             subtype='mail.mt_comment')

    @api.model
    def create(self, vals):
        mproduct = super(MisProduct, self).create(vals)
        group_name = 'Investment'
        group_id = 0
        if vals.get('investment_ok') == True:
            group_tag = self.env['mis.analytic.tag.group'].search([('name', '=', group_name)])
            if group_tag:
                for gr in group_tag:
                    group_id = gr.id
            else:
                group_tag = self.env['mis.analytic.tag.group'].create({'name': group_name})
                group_id = group_tag.id
            intrate = vals.get('interest_rate') or self.interest_rate
            if intrate < 0 or intrate > 100:
                raise UserError('Interest Rete should be between 0-100')
            code = vals['name']
            if not mproduct.invest_analytic_tag_ids:
                obj_analytic_tag_ids = self.env['account.analytic.tag'].search([
                    ('name', '=', code), ('analytic_tag_group', '=', group_id)],limit=1)

                if obj_analytic_tag_ids == True:
                    pro_analytic_tag_ids = obj_analytic_tag_ids
                else:
                    pro_analytic_tag_ids = self.env['account.analytic.tag'].create({
                        'name': code, 'analytic_tag_group': group_id, 'company_id': self.env.company.id, })
                mproduct.invest_analytic_tag_ids = pro_analytic_tag_ids.ids
        return mproduct

    def action_custom_exapense_show(self):
        journal_entry = []
        journal_items = self.env['account.move.line'].search(
            [('analytic_tag_ids', 'in', self.invest_analytic_tag_ids.ids), ('parent_state', '=', 'posted'), ('account_id.internal_group', 'in', ['expense', 'income'])])
        for j in journal_items:
            journal_entry.append(j.id)
        return {
            'name': _('Journal Items'),
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', journal_entry)],
        }

    def write(self, vals):
        mproduct = super(MisProduct, self).write(vals)
        temproduct = self.env['product.template'].search([('id', '=', self.id)])
        productname = temproduct.name
        investment_ok = vals.get('investment_ok') or self.investment_ok
        intrate = vals.get('interest_rate') or self.interest_rate
        if intrate < 0 or intrate > 100:
            raise UserError('Interest Rete should be between 0-100')

        if vals.get('interest_rate') == True or productname != self.name:
            group_id = 0
            group_name = 'Investment'

            group_tag = self.env['mis.analytic.tag.group'].search([('name', '=', group_name)])
            if group_tag:
                for gr in group_tag:
                    group_id = gr.id
            else:
                group_tag = self.env['mis.analytic.tag.group'].create({'name': group_name})
                group_id = group_tag.id
            code = self.name
            
            if not self.invest_analytic_tag_ids:
                obj_analytic_tag_ids = self.env['account.analytic.tag'].search([
                    ('name', '=', productname), ('analytic_tag_group', '=', group_id)])

                if obj_analytic_tag_ids == True:
                    pro_analytic_tag_ids = obj_analytic_tag_ids.write({
                        'name': code, 'analytic_tag_group': group_id, 'company_id': self.env.company.id, })
                else:
                    pro_analytic_tag_ids = self.env['account.analytic.tag'].create({
                        'name': code, 'analytic_tag_group': group_id, 'company_id': self.env.company.id, })

                self.invest_analytic_tag_ids = pro_analytic_tag_ids.ids

        return mproduct


class MisInvClassification(models.Model):
    _name = 'mis.inv.classfication'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Classification'

    name = fields.Char(string="Classification", track_visibility='onchange')
    clasificationpercentage = fields.Float(string="Classification %", defualt=0.00)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Classfication already exists !"),
    ]


class MisInvRiskRate(models.Model):
    _name = 'mis.inv.riskrate'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Risk Rate'

    name = fields.Char(string="Risk Rate", track_visibility='onchange')
    ratepercentage = fields.Float(string="Risk %", defualt=0.00)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Risk Rate already exists !"),
    ]


class MisInvLiquidityReturn(models.Model):
    _name = 'mis.inv.liquidityreturn'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Liquidity Return'

    name = fields.Char(string="Liquidity Return", track_visibility='onchange')
    returnpercentage = fields.Float(string="Retern %", defualt=0.00)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Liquidity Return already exists !"),
    ]


class MisInvGeographic(models.Model):
    _name = 'mis.inv.geographic'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Geographic'

    name = fields.Char(string="Geographic", track_visibility='onchange')
    geographicpercentage = fields.Float(string="Geographic %", defualt=0.00)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Geographic already exists !"),
    ]


class MisInvType(models.Model):
    _name = 'mis.inv.type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Type'

    name = fields.Char(string="Type", track_visibility='onchange')
    typepercentage = fields.Float(string="Retern %", defualt=0.00)
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Type already exists !"),
    ]
