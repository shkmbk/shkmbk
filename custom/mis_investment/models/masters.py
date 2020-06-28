
from odoo import models, fields, api, _
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
            code = vals['name']
            pro_analytic_tag_ids = self.env['account.analytic.tag'].create({
                'name': code, 'analytic_tag_group': group_id,})
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


        if vals.get('investment_ok') == True or productname!=self.name:
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

