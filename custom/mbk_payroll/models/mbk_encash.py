from odoo import models, fields, api, _
from datetime import date
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import format_date


class MbkEncash(models.Model):
    _name = 'mbk.encash'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Employee Leave Encashment'
    _order = 'date_to desc'

    encash_no = fields.Char(string='Number', readonly=True, store=True, default='New')
    name = fields.Char(string='Name', readonly=True, store=True)
    number = fields.Char(string='Reference', readonly=True, required=True, copy=False,
                         states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True,
                                  states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, track_visibility='onchange', default='draft',
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""")
    note = fields.Text(string='Internal Note', readonly=True,
                       states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    contract_id = fields.Many2one('hr.contract', string='Contract', readonly=True,
                                  states={'draft': [('readonly', False)], 'verify': [('readonly', False)]},
                                  domain="[('company_id', '=', company_id)]")
    employee_code = fields.Char(string='Code', readonly=True)
    date = fields.Date('Date', default=fields.Date.to_string(date.today()),
                       states={'draft': [('readonly', False)], 'verify': [('readonly', False)]}, readonly=True,
                       help="Keep empty to use the period of the validation(Payslip) date.")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True)
    date_to = fields.Date(string='As on Date', readonly=True, required=True,
                          states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    date_effective = fields.Date(string='Effective Date', readonly=True, store=True, required=True,
                                 states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    al_provision_amount = fields.Float(string='Provision Amount', readonly=True, store=True, default=False)
    al_provision_date = fields.Date(string='Last Provision Booking Date', readonly=True, store=True, default=False)
    warning_message = fields.Char(readonly=True)
    encash_amount = fields.Float(string='Leave Salary', readonly=True, compute='compute_encash_amount', store=True,
                                 default=False)
    ticket_allowance = fields.Float(string='Ticket Allowance', readonly=True, store=True, default=False)
    ticket_amount = fields.Float(string='Ticket Amount', default=False)
    net_amount = fields.Float(string='Net Encash', compute='compute_net_amount', store=True, default=False)
    join_date = fields.Date(string='Date Of Join', readonly=True, store=True, default=False)
    basic_salary = fields.Float(string='Basic Salary', readonly=True, store=True, default=False)
    allowances = fields.Float(string='Allowance', readonly=True, store=True, default=False)
    net_salary = fields.Float(string='Net Salary', readonly=True, store=True, default=False)
    total_days = fields.Float(string='Total Working Days', readonly=True, store=True, default=False)
    lop_days = fields.Float(string='LOP Days', readonly=True, store=True, default=False)
    eligible_days = fields.Float(string='Eligible Days', readonly=True, default=False)
    op_days = fields.Float(string='Opening Leave Days', readonly=True, store=True, default=False)
    new_days = fields.Float(string='New Leave Days', readonly=True, store=True, default=False)
    leave_taken = fields.Float(string='Leave Taken', readonly=True, store=True, default=False)
    encashed_days = fields.Float(string='Encashed Days', readonly=True, store=True, default=False)
    available_days = fields.Float(string='Available Leave Days', readonly=True, store=True, default=False)
    encash_days = fields.Float(string='Encashing Days', required=True, store=True, default=False,
                               track_visibility='onchange')
    balance_days = fields.Float(string='Balance Days', readonly=True, compute='compute_al_balance', store=True,
                                default=False)
    job_id = fields.Many2one('hr.job', string='Designation', readonly=True, store=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True, store=True)
    bank_name = fields.Char(string='Bank', readonly=True, store=True)
    iban_no = fields.Char(string="IBAN Number", readonly=True, store=True)

    def compute_sheet(self):
        employee_id = self.employee_id
        join_date = self.join_date
        op_al_days = self.op_days
        contract_id = self.contract_id
        op_fy_date = datetime(2020, 6, 1).date()
        as_on_date = self.date_to

        # Checking wheather contract end date mentioned
        if contract_id.date_end:
            to_date = contract_id.date_end
        else:
            to_date = as_on_date

        total_days = (to_date - join_date).days + 1
        op_eligible_days = employee_id.op_eligible_days

        if join_date < op_fy_date:
            op_lop_days = (op_fy_date - join_date).days - op_eligible_days
            c_total_days = (to_date - op_fy_date).days + 1
        else:
            op_lop_days = 0
            c_total_days = (to_date - join_date).days + 1
        # LOP Leaves in Currecnt Period
        objlopleave = self.env['hr.leave'].search(
            [('employee_id', '=', employee_id.id), ('state', '=', 'validate'), ('holiday_status_id.unpaid', '=', 1),
             ('request_date_from', '<=', to_date)])
        c_lop = 0.00
        for lop in objlopleave:
            if lop.request_date_to <= to_date:
                c_lop += lop.number_of_days
            else:
                c_lop += (to_date - lop.request_date_from).days + 1
        # Annual Leave Taken
        objalleave = self.env['hr.leave'].search(
            [('employee_id', '=', employee_id.id), ('state', '=', 'validate'), ('holiday_status_id', '=', 1),
             ('request_date_from', '<=', to_date)])
        c_alt = 0.00
        for al in objalleave:
            if al.request_date_to <= to_date:
                c_alt += al.number_of_days
            else:
                c_alt += (to_date - al.request_date_from).days + 1
        # Encashed Days
        encashed_days = 0.0
        objencash = self.env['mbk.encash'].search([('employee_id', '=', employee_id.id), ('state', '!=', 'cancel')])
        for en in objencash:
            if en.id != self.id:
                encashed_days += en.encash_days
        lop_days = op_lop_days + c_lop

        if join_date < op_fy_date:
            eligible_days = op_eligible_days + c_total_days - c_lop
        else:
            eligible_days = c_total_days - c_lop
        c_eligible_days = c_total_days - c_lop
        new_al_days = 0.00
        if eligible_days > 182:
            new_al_days = (c_eligible_days * 30 / 365)
            annualleave_days = round(op_al_days + new_al_days - (c_alt + encashed_days), 2)
        else:
            annualleave_days = 0.00

        self.total_days = total_days
        self.eligible_days = eligible_days
        self.lop_days = lop_days
        self.op_days = op_al_days
        self.new_days = new_al_days
        self.leave_taken = c_alt
        self.encashed_days = encashed_days
        self.available_days = annualleave_days
        self.write({'state': 'verify'})

        return True

    def button_cancel(self):
        self.state = 'cancel'

    def action_encash_cancel(self):
        if self.filtered(lambda slip: slip.state == 'done'):
            raise UserError(_("Cannot cancel a payslip that is done."))
        self.write({'state': 'cancel'})

    def action_encash_draft(self):
        return self.write({'state': 'draft'})

    def action_encash_done(self):
        if self.encash_days <= 0:
            raise UserError('Enter valid Leave Encash Days')

        if self.encash_no == 'New':
            self.encash_no = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(
                'mbk.encash') or _('New')
        return self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        vals['state'] = 'draft'
        res = super(MbkEncash, self).create(vals)
        return res

    def unlink(self):
        for encash in self:
            if encash.state not in ('draft', 'cancel') and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been posted."))
            encash.trans_line.unlink()
        return super(MbkEncash, self).unlink()

    @api.onchange('employee_id', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_to):
            return

        employee = self.employee_id
        date_to = self.date_to
        al_provision_date = date_to

        if not self.contract_id or self.employee_id != self.contract_id.employee_id:  # Add a default contract if not already defined
            contracts = employee._get_contracts(date_to, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id
        contract_id = self.contract_id

        self.employee_code = employee.registration_number
        self.join_date = employee.date_of_join
        self.al_provision_date = date_to
        self.company_id = employee.company_id
        self.basic_salary = contract_id.wage
        self.allowances = contract_id.x_other_allowance
        self.net_salary = contract_id.wage + contract_id.x_other_allowance
        self.op_days = employee.op_leave_days
        self.job_id = employee.job_id
        self.department_id = employee.department_id
        self.bank_name = employee.agent_id.name
        self.iban_no = employee.iban_number

        encash_name = 'Leave Encash'
        self.name = '%s - %s - %s' % (encash_name, self.employee_id.name or '', format_date(self.env, self.date_to, date_format="MMMM y"))

        if date_to > al_provision_date:
            self.warning_message = _(
                "This Encash computation can be erroneous! Provision entries not be generated after %s." %
                (al_provision_date))
        else:
            self.warning_message = False

    @api.depends('available_days', 'encash_days')
    def compute_al_balance(self):
        self.balance_days = self.available_days - self.encash_days

    @api.depends('encash_days', 'net_salary')
    def compute_encash_amount(self):
        perday_rate = self.net_salary * 12 / 365
        self.encash_amount = round(perday_rate * self.encash_days, 2)

    @api.depends('encash_amount', 'ticket_amount')
    def compute_net_amount(self):
        self.net_amount = round(self.encash_amount + self.ticket_amount, 2)
