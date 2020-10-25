from odoo import models, fields, api
from datetime import date
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError, Warning
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta


class MbkBudget(models.Model):
    _name = 'mbk.budget'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Fund Flow Forecast'
    _order = 'date_to desc'

    @api.model
    def _default_opening_balance(self):
        # Search last bank statement and set current opening balance as closing balance of previous one
        obj_last_budget = self.env['mbk.budget'].search([('state', 'in', ['done', 'verify'])], order='date_to desc',
                                                        limit=1)
        if obj_last_budget:
            if obj_last_budget.state == 'done':
                return obj_last_budget.balance_end_real
            else:
                return obj_last_budget.balance_end
        return 0

    budget_no = fields.Char(string='Number', readonly=True, store=True, copy=False, default='New')
    name = fields.Char(string='Name', copy=False, store=True)
    # number = fields.Char(string='Reference', readonly=True, required=True, copy=False,
    #                    states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Active'),
        ('done', 'Done'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, track_visibility='onchange', default='draft',
        help="""* When the budget is created the status is \'Draft\'
                \n* If the budget period is under running, the status is \'Running\'.
                \n* If the budget period completed then status is set to \'Done\'.
                \n* When user cancel budget the status is \'Rejected\'.""")
    note = fields.Text(string='Internal Note', readonly=True,
                       states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    date = fields.Date('Date', default=fields.Date.to_string(date.today()),
                       states={'draft': [('readonly', False)], 'verify': [('readonly', False)]}, readonly=True,
                       copy=False,
                       help="Keep empty to use the period of the validation(budget) date.")
    company_id = fields.Many2one('res.company', 'Company', readonly=True, copy=False, required=True,
                                 default=lambda self: self.env.company)
    date_from = fields.Date(string='From', readonly=True, required=True, copy=False,
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    date_to = fields.Date(string='To', readonly=True, required=True, copy=False,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
                          states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    balance_start = fields.Float(string='Opening Balance', help="Budget starting balance",
                                 states={'done': [('readonly', True)]}, default=_default_opening_balance, copy=False)
    balance_start_real = fields.Float(string='Starting Balance', help="Actual starting balance",
                                      states={'done': [('readonly', True)]}, default=0.00, copy=False)
    balance_end_real = fields.Float('Ending Balance', help="Actual ending balance", compute='_compute_end_real', store=True, copy=False, readonly=True)
    balance_end_variance = fields.Float('Net Variance', compute='_compute_end_variance', store=True, copy=False, readonly=True)
    balance_end = fields.Float('Closing Balance', compute='_compute_end_balance', store=True, copy=False,
                               help='Budget Closing Balance as calculated based on Opening Balance and transaction lines')
    in_line_ids = fields.One2many('mbk.budget.in_flow', 'mbk_budget_id', string='Fund In Flow lines',
                                  states={'done': [('readonly', True)]}, copy=True)
    out_line_ids = fields.One2many('mbk.budget.out_flow', 'mbk_budget_id', string='Fund Out Flow lines',
                                   states={'done': [('readonly', True)]}, copy=True)
    net_fund_position = fields.Monetary(string='Net Fund Position', readonly=True, compute='_compute_net_fund',
                                        store=True, default=False)
    net_fund_actual = fields.Monetary(string='Net Fund Actual', readonly=True, compute='_compute_net_fund_actual',
                                      store=True, default=False)
    inflow_budget = fields.Monetary(string='Budget Inflow', readonly=True, compute='_compute_net_fund',
                                    store=True, default=False)
    outflow_budget = fields.Monetary(string='Budget Outflow', readonly=True, compute='_compute_net_fund',
                                     store=True, default=False)
    inflow_actual = fields.Monetary(string='Actual Inflow', readonly=True, compute='_compute_net_fund_actual',
                                    store=True, default=False)
    outflow_actual = fields.Monetary(string='Actual Outflow', readonly=True, compute='_compute_net_fund_actual',
                                     store=True, default=False)
    required_fund_budget = fields.Monetary(string='Required Fund')
    required_fund_actual = fields.Monetary(string='Approved Fund')
    currency_id = fields.Many2one('res.currency', String='Currency', Default=131, store=True)

    def compute_sheet(self):
        if not self.in_line_ids and not self.out_line_ids:
            raise UserError("Please enter budget Inflow & Outflow before computation.")
        if self.net_fund_position < 0:
            net_fund_position = abs(self.net_fund_position)
            mod = 1000
            mod_value = (net_fund_position % mod)
            if mod_value > 0:
                net_fund_position = (net_fund_position - mod_value) + mod
            required_fund_budget = net_fund_position
        else:
            required_fund_budget = 0.00
        self.required_fund_budget = required_fund_budget

        if self.budget_no == 'New':
            self.budget_no = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(
                'mbk.budget') or _('New')

        self.state = 'verify'
        return True

    def button_cancel(self):
        self.state = 'cancel'

    def action_budget_cancel(self):
        if self.filtered(lambda slip: slip.state == 'done'):
            raise UserError("Cannot cancel a budget that is done.")
        self.write({'state': 'cancel'})

    def action_budget_draft(self):
        return self.write({'state': 'draft'})

    def action_budget_done(self):
        if self.net_fund_actual == self.balance_start:
            raise UserError('Enter actual inflow & Outflow before finalization')
        if not self.required_fund_actual or self.required_fund_actual == 0:
            if self.required_fund_budget > 0:
                raise UserError('Enter Approved Fund Details')

        return self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        obj_last_budget = self.env['mbk.budget'].search([('state', '=', 'draft')])
        if obj_last_budget:
            raise UserError('Finalize the previous budget')
        vals['state'] = 'draft'
        res = super(MbkBudget, self).create(vals)
        return res

    def unlink(self):
        for budget in self:
            if budget.state not in ('draft', 'cancel') and not self._context.get('force_delete'):
                raise UserError("You cannot delete an entry which has been posted.")
            budget.trans_line.unlink()
        return super(MbkBudget, self).unlink()

    @api.depends('balance_start', 'in_line_ids.budget_amount', 'out_line_ids.budget_amount')
    def _compute_net_fund(self):
        for budget in self:
            inflow_budget = 0.00
            outflow_budget = 0.00
            balance_start = 0.00

            if budget.balance_start:
                balance_start = budget.balance_start

            for line in budget.in_line_ids:
                inflow_budget += line.budget_amount

            for line in budget.out_line_ids:
                outflow_budget += line.budget_amount

            net_fund_position = balance_start + inflow_budget - outflow_budget
            budget.update({
                'inflow_budget': inflow_budget,
                'outflow_budget': outflow_budget,
                'net_fund_position': net_fund_position,
            })

    @api.depends('balance_start_real', 'in_line_ids.actual_amount', 'out_line_ids.actual_amount')
    def _compute_net_fund_actual(self):
        for budget in self:
            balance_start_real = 0.00
            inflow_actual = 0.00
            outflow_actual = 0.00

            if budget.balance_start_real:
                balance_start_real = budget.balance_start_real

            for line in budget.in_line_ids:
                inflow_actual += line.actual_amount

            for line in budget.out_line_ids:
                outflow_actual += line.actual_amount

            net_fund_actual = balance_start_real + inflow_actual - outflow_actual

            budget.update({
                'inflow_actual': inflow_actual,
                'outflow_actual': outflow_actual,
                'net_fund_actual': net_fund_actual,
            })

    @api.depends('net_fund_position', 'required_fund_budget')
    def _compute_end_balance(self):
        for budget in self:
            if budget.required_fund_budget:
                required_fund_budget = budget.required_fund_budget
            else:
                required_fund_budget = 0.00
            balance_end = budget.net_fund_position + required_fund_budget

            budget.update({
                'balance_end': balance_end,
            })

    @api.depends('net_fund_actual', 'required_fund_actual')
    def _compute_end_real(self):
        for budget in self:
            if budget.required_fund_actual:
                required_fund_actual = budget.required_fund_actual
            else:
                required_fund_actual = 0.00

            balance_end_real = budget.net_fund_actual + required_fund_actual

            budget.update({
                'balance_end_real': balance_end_real,
            })

    @api.depends('balance_end_real', 'balance_end')
    def _compute_end_variance(self):
        for budget in self:
            balance_end_variance = budget.balance_end_real + budget.balance_end
            budget.update({
                'balance_end_variance': balance_end_variance,
            })


    def get_opening_balance(self):
        # Search last bank statement and set current opening balance as closing balance of previous one
        obj_last_budget = self.env['mbk.budget'].search([('state', 'in', ['done'])], order='date_to desc',
                                                        limit=1)
        if obj_last_budget:
            if obj_last_budget.state == 'done':
                self.balance_start_real = obj_last_budget.balance_end_real
            else:
                self.balance_start_real = 0.00

class MBKBudgetInFlow(models.Model):
    _name = 'mbk.budget.in_flow'
    _description = 'Fund In Flow'
    _order = 'mbk_budget_id, sl_no, id'

    mbk_budget_id = fields.Many2one('mbk.budget', string='Budget', required=True, ondelete='cascade', index=True)
    sl_no = fields.Integer(string='Sl', required=True, index=True, readonly=True, default=10)
    mbk_project_id = fields.Many2one('mbk.inv.projects', string='Projects', required=True,
                                     domain="[('is_inflow', '=', True)]")
    name = fields.Char(string='Description', store=True)
    budget_amount = fields.Float(string='Budget')
    actual_amount = fields.Float(string='Actual')
    variance_amount = fields.Float(string='Variance', readonly=True, compute='_calculate_variance',
                                   store=True, default=False)

    @api.depends('budget_amount', 'actual_amount')
    def _calculate_variance(self):
        for rec in self:
            rec.variance_amount = rec.budget_amount - rec.actual_amount

    @api.onchange('mbk_project_id')
    def _default_description(self):
        for rec in self:
            if rec.mbk_project_id and not rec.name:
                rec.name = rec.mbk_project_id.description


class MBKBudgetOutFlow(models.Model):
    _name = 'mbk.budget.out_flow'
    _description = 'Fund Out Flow'
    _order = 'mbk_budget_id, sl_no, id'

    mbk_budget_id = fields.Many2one('mbk.budget', string='Budget', required=True, ondelete='cascade', index=True)
    sl_no = fields.Integer(string='Sl', required=True, index=True, readonly=True, default=10)
    mbk_project_id = fields.Many2one('mbk.inv.projects', string='Projects', required=True,
                                     domain="[('is_outflow', '=', True)]")
    name = fields.Char(string='Description', store=True)
    budget_amount = fields.Float(string='Budget')
    actual_amount = fields.Float(string='Actual')
    variance_amount = fields.Float(string='Variance', readonly=True, compute='_calculate_variance',
                                   store=True, default=False)

    @api.depends('budget_amount', 'actual_amount')
    def _calculate_variance(self):
        for rec in self:
            rec.variance_amount = rec.actual_amount - rec.budget_amount

    @api.onchange('mbk_project_id')
    def _default_description(self):
        for rec in self:
            if rec.mbk_project_id and not rec.name:
                rec.name = rec.mbk_project_id.description


class MBKProjects(models.Model):
    _name = 'mbk.inv.projects'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Projects Master For Budget'

    name = fields.Char(string="Projects", track_visibility='onchange')
    description = fields.Char(string="Description")
    is_inflow = fields.Boolean(string="In Flow")
    is_outflow = fields.Boolean(string="Out Flow")
    is_project = fields.Boolean(string="Project")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Type already exists !"),
    ]
