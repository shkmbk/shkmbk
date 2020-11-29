from odoo import models, fields, api
from datetime import date
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta


class MbkHR(models.Model):
    _name = 'mbk.hr'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Employee And Payroll Summary For The Month'
    _order = 'date_to desc'

    name = fields.Char(string='Name', readonly=True, store=True, default='New')
    date = fields.Date('Date', default=fields.Date.to_string(date.today()),
                       states={'draft': [('readonly', False)]}, readonly=True,
                       help="Keep empty to use the period of the validation(Payslip) date.")
    ref = fields.Char(string='Reference', readonly=True, copy=False,
                      states={'draft': [('readonly', False)]})
    date_from = fields.Date(string='From', readonly=True, required=True, copy=False,
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='To', readonly=True, required=True, copy=False,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
                          states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=3)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, tracking=True, default='draft')
    note = fields.Text(string='Internal Note', readonly=True,
                       states={'draft': [('readonly', False)]})
    total_opening = fields.Integer(string="Total Opening Employees", compute='_compute_net_closing', store=True, Default=False)
    total_new = fields.Integer(string="Total New Joinee", compute='_compute_net_closing', store=True, Default=False)
    total_exit = fields.Integer(string="Total Termination/Resignation", compute='_compute_net_closing', store=True, Default=False)
    total_closing = fields.Integer(string="Total Termination/Resignation", compute='_compute_net_closing', store=True, Default=False)
    total_salary = fields.Float(string='Total Salary', readonly=True, compute='_compute_net_closing', store=True, default=False)
    total_deductions = fields.Float(string='Total Deductions', readonly=True, compute='_compute_net_closing', store=True, default=False)
    total_leave_salary = fields.Float(string='Total Leave Salary', readonly=True, compute='_compute_net_closing', store=True, default=False)
    total_net_salary = fields.Float(string='Total Net Salary', readonly=True, compute='_compute_net_closing', store=True, default=False)
    currency_id = fields.Many2one('res.currency', String='Currency', Default=131, store=True)
    line_ids = fields.One2many('mbk.hr.line', 'mbk_hr_id',
                               string='Payroll Summary', copy=True, readonly=True,
                               states={'draft': [('readonly', False)]})

    def action_load_sheet(self):
        as_on_date = self.date_to
        # as_on_date_str = datetime.strptime(date_to, '%Y-%m-%d').date()
        op_fy_date = datetime(2020, 6, 1).date()

        if not self.ref:
            self.ref = 'Employee Summary for ' + (self.date_to).strftime("%B %Y")
        # delete old esob provision lines
        if self.state in ('draft'):
            self.line_ids.unlink()

        obj_analytic_account = self.env['account.analytic.account'].search(
            [('company_id', '=', 3)], order='id')
        if not obj_analytic_account:
            raise UserError('There are no analytic account found for selected parameters')
        new_lines = self.env['mbk.hr.line']

        sl_no = 0
        total_opening = 0.00
        for rec in obj_analytic_account:
            previous_month = self.env['mbk.hr.line'].search(
                [('analytic_account_id', '=', rec.id), ('to_date', '<=', self.date_from)], order='to_date desc',
                limit=1)
            if previous_month:
                opening = previous_month.closing
            else:
                opening = 0
            total_opening += opening
            sl_no += 1
            values = {
                'mbk_hr_id': self.id,
                'sl_no': sl_no,
                'analytic_account_id': rec.id,
                'opening_nos': opening,
                'new_nos': 0,
                'exit_nos': 0,
                'closing_nos': opening,
                'salary': 0.00,
                'deductions': 0.00,
                'leave_salary': 0.00,
                'net_salary': 0.00,
                'to_date': as_on_date
            }
            new_lines.create(values)
        # self.total_opening = total_opening
        # self.total_closing = total_opening
        return new_lines

    def action_hr_cancel(self):
        if self.filtered(lambda slip: slip.state == 'post'):
            raise UserError(_("Cannot cancel a payroll summary is post."))
        self.write({'state': 'cancel'})

    def action_hr_draft(self):
        return self.write({'state': 'draft'})

    def action_post(self):
        if self.name == 'New':
            self.name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(
                'mbk.hr') or _('New')
        return self.write({'state': 'posted'})

    @api.model
    def create(self, vals):
        vals['state'] = 'draft'
        res = super(MbkHR, self).create(vals)
        return res

    def unlink(self):
        for hr in self:
            if hr.state not in ('draft') and not self._context.get('force_delete'):
                raise UserError("You cannot delete an entry which has been posted.")
            hr.line_ids.unlink()
        return super(MbkHR, self).unlink()

    @api.depends('line_ids.closing_nos')
    def _compute_net_closing(self):
        for hr in self:
            tot_opening = 0.00
            tot_new = 0.00
            tot_exit = 0.00
            tot_closing = 0.00
            tot_salary = 0.00
            tot_deductions = 0.00
            tot_leave_salary = 0.00
            tot_net_salary = 0.00

            for line in hr.line_ids:
                tot_opening += line.opening_nos
                tot_new += line.new_nos
                tot_exit += line.exit_nos
                tot_closing += line.closing_nos
                tot_salary += line.salary
                tot_deductions += line.deductions
                tot_leave_salary += line.leave_salary
                tot_net_salary += line.net_salary

            hr.update({
                'total_opening': tot_opening,
                'total_new': tot_new,
                'total_exit': tot_exit,
                'total_closing': tot_closing,
                'total_salary': tot_salary,
                'total_deductions': tot_deductions,
                'total_leave_salary': tot_leave_salary,
                'total_net_salary': tot_net_salary,

            })


class MbkHRLine(models.Model):
    _name = 'mbk.hr.line'
    _description = 'HR Line'
    _order = 'mbk_hr_id, sl_no'

    mbk_hr_id = fields.Many2one('mbk.hr', string='HR Summary', required=True, ondelete='cascade', index=True)
    sl_no = fields.Integer(string='Sl', required=True, readonly=True, default=10)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True,
                                          readonly=True)
    opening_nos = fields.Integer(string='Opening')
    new_nos = fields.Integer(string='New Joinee')
    exit_nos = fields.Integer(string='Termination/Resignation')
    closing_nos = fields.Integer(string='Closing', compute='_get_closing', store=True, default=False)
    salary = fields.Float(string='Salary')
    deductions = fields.Float(string='Deductions')
    leave_salary = fields.Float(string='Leave Salary')
    net_salary = fields.Float(string='Net Salary', compute='_get_net_salary', store=True, default=False)
    remarks = fields.Char(string='Remarks')
    to_date = fields.Date(string='To Date', readonly=True)

    @api.depends('opening_nos', 'new_nos', 'exit_nos')
    def _get_closing(self):
        for rec in self:
            rec.closing_nos = rec.opening_nos + rec.new_nos - rec.exit_nos

    @api.depends('salary', 'deductions', 'leave_salary')
    def _get_net_salary(self):
        for rec in self:
            rec.net_salary = rec.salary + rec.leave_salary - rec.deductions
