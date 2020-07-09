
from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError, UserError

class MisProduct(models.Model):
    _inherit = 'product.template'

    def _suminvestexpense(self):
        objJournal = self.env['account.move.line'].search([('analytic_tag_ids', 'in', self.invest_analytic_tag_ids.ids)])
        sum=0.00
        for jor in objJournal:
            sum+=jor.balance
        self.sum_invest_expense= sum

    investment_ok = fields.Boolean(string="Can be Investment",   track_visibility='onchange')
    isdeposit = fields.Boolean(string="Is Deposit?",   track_visibility='onchange')
    deposit_date = fields.Date(string="Deposit Date", track_visibility='onchange')
    maturity_date = fields.Date(string="Maturity date", track_visibility='onchange')
    classification_id = fields.Many2one('mis.inv.classfication', string="Classification")
    risk_id = fields.Many2one('mis.inv.riskrate', string="Risk")
    liquidityreturn_id = fields.Many2one('mis.inv.liquidityreturn', string="Liquidity Return")
    geographic_id = fields.Many2one('mis.inv.geographic', string="Geographic")
    responsibility_id = fields.Many2one('res.partner', string="Responsibility")
    invest_analytic_tag_id = fields.Many2one('account.analytic.tag', string='Analytic Tags')
    invest_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    sum_invest_expense = fields.Float(string="Total Expenses", compute='_suminvestexpense')
    bank_journal = fields.Many2one('account.journal', string="Bank Account",  domain=" [('type', '=', 'bank')]")
    interest_rate =fields.Float(string="Interest Rate")
    day_in_a_year = fields.Integer(string="No of Days in Year")
    expected_earning = fields.Float(string="Expected Earning")
#    expected_earning_new = fields.Float(string="Expected Earning", compute='calculate_interest', store=True)

    @api.depends('interest_rate', 'day_in_a_year', 'deposit_date', 'maturity_date')
    def calculate_interest(self):
        for rec in self:
            tot_expect_earning =0.00
            if rec.interest_rate>0 and rec.day_in_a_year>0:
                if rec.deposit_date and rec.maturity_date and rec.isdeposit==True:
                    totdays = (rec.maturity_date - rec.deposit_date).days
                    tot_expect_earning =rec.standard_price*(rec.interest_rate/(rec.day_in_a_year*100))*totdays
                    rec.expected_earning = tot_expect_earning


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
            if intrate<0 or intrate>100:
                raise UserError('Interest Rete should be between 0-100')
            code = vals['name']

            obj_analytic_tag_ids = self.env['account.analytic.tag'].search([
                ('name', '=', code), ('analytic_tag_group', '=', group_id)])

            pro_analytic_tag_ids = obj_analytic_tag_ids
            if obj_analytic_tag_ids==True:
                pro_analytic_tag_ids=obj_analytic_tag_ids
            else:
                pro_analytic_tag_ids = self.env['account.analytic.tag'].create({
                    'name': code, 'analytic_tag_group': group_id, })
#            pro_analytic_tag_ids = self.env['account.analytic.tag'].create({
#                'name': code, 'analytic_tag_group': group_id,})
            mproduct.invest_analytic_tag_ids = pro_analytic_tag_ids.ids + mproduct.invest_analytic_tag_ids.ids
        return mproduct

    def action_custom_exapense_show(self):
        journal_entry = []
        journal_items = self.env['account.move.line'].search([('analytic_tag_ids','in',self.invest_analytic_tag_ids.ids)])
        for j in journal_items:
            journal_entry.append(j.move_id.id)
        return {
            'name': _('Journal Entries'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', journal_entry)],
        }

    def write(self, vals):
        mproduct = super(MisProduct, self).write(vals)
        temproduct = self.env['product.template'].search([('id', '=', self.id)])
        productname =temproduct.name
        investment_ok = vals.get('investment_ok') or self.investment_ok
        intrate = vals.get('interest_rate') or self.interest_rate
        if intrate < 0 or intrate > 100:
            raise UserError('Interest Rete should be between 0-100')

        if vals.get('interest_rate') == True or productname!=self.name:
            group_id = 0
            group_name='Investment'


            group_tag = self.env['mis.analytic.tag.group'].search([('name', '=', group_name)])
            if group_tag:
               for gr in group_tag:
                    group_id = gr.id
            else:
                group_tag = self.env['mis.analytic.tag.group'].create({'name': group_name})
                group_id = group_tag.id
            code = self.name

            obj_analytic_tag_ids = self.env['account.analytic.tag'].search([
                ('name', '=', productname), ('analytic_tag_group', '=', group_id)])

            if obj_analytic_tag_ids==True:
                pro_analytic_tag_ids = obj_analytic_tag_ids.write({
                    'name': code, 'analytic_tag_group': group_id,})
            else:
                pro_analytic_tag_ids = self.env['account.analytic.tag'].create({
                    'name': code, 'analytic_tag_group': group_id, })

            self.invest_analytic_tag_ids = pro_analytic_tag_ids.ids

        return mproduct


class MisInvClassification(models.Model):
    _name = 'mis.inv.classfication'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description ='Classification'

    name = fields.Char(string="Classification",  track_visibility='onchange')
    clasificationpercentage = fields.Float(string="Classification %", defualt=0.00)

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Classfication already exists !"),
    ]
class MisInvRiskRate(models.Model):
    _name = 'mis.inv.riskrate'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description ='Risk Rate'

    name = fields.Char(string="Risk Rate",  track_visibility='onchange')
    ratepercentage = fields.Float(string="Risk %", defualt=0.00)

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Risk Rate already exists !"),
    ]
class MisInvLiquidityReturn(models.Model):
    _name = 'mis.inv.liquidityreturn'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description ='Liquidity Return'

    name = fields.Char(string="Liquidity Return",  track_visibility='onchange')
    returnpercentage = fields.Float(string="Retern %", defualt=0.00)

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Liquidity Return already exists !"),
    ]
class MisInvGeographic(models.Model):
    _name = 'mis.inv.geographic'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description ='Geographic'

    name = fields.Char(string="Geographic",  track_visibility='onchange')
    geographicpercentage = fields.Float(string="Geographic %", defualt=0.00)

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Geographic already exists !"),
    ]

