from odoo import models, fields, api
from datetime import date
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import format_date


class MbkESOB(models.Model):
    _name = 'mbk.esob'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Employee End of Settlement'
    _order = 'date_to desc'

    esob_no = fields.Char(string='Number', readonly=True, store=True, default='New')
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
    al_provision_days = fields.Float(string='Provision Days', readonly=True, store=True, default=False)
    al_provision_amount = fields.Float(string='Provision Amount', readonly=True, store=True, default=False)
    al_provision_date = fields.Date(string='Provision', readonly=True, store=True, default=False)
    esob_provision_amount = fields.Float(string='Provision Amount', readonly=True, store=True, default=False)
    esob_provision_date = fields.Date(string='Provision Date', readonly=True, store=True, default=False)
    esob_provision_days = fields.Float(string='Provision Amount', readonly=True, store=True, default=False)
    warning_message = fields.Char(readonly=True)
    encash_amount = fields.Float(string='Leave Salary', readonly=True, compute='compute_encash_amount', store=True,
                                 default=False)
    esob_amount = fields.Float(string='ESOB Amount', readonly=True, compute='compute_esob_amount', store=True,
                               default=False)
    ticket_allowance = fields.Float(string='Ticket Allowance', readonly=True, store=True, default=False)
    ticket_amount = fields.Float(string='Ticket Amount', default=False)
    net_amount = fields.Float(string='Net ESOB', compute='compute_net_amount', store=True, default=False)
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
    avl_encash_days = fields.Float(string='Available Leave Days', readonly=True, store=True, default=False)
    avl_esob_days = fields.Float(string='Available ESOB Days', readonly=True, store=True, default=False)
    encash_days = fields.Float(string='Encashing Days', required=True, store=True, default=False)
    esob_days = fields.Float(string='ESOB Days', required=True, store=True, default=False)
    job_id = fields.Many2one('hr.job', string='Designation', readonly=True, store=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True, store=True)
    bank_name = fields.Char(string='Bank', readonly=True, store=True)
    iban_no = fields.Char(string="IBAN Number", readonly=True, store=True)
    payslip_ids = fields.Many2many('hr.payslip', string='Pay Slip', domain="[('employee_id', '=', employee_id)]")
    line_ids = fields.One2many('mbk.esob.line', 'esob_id',
                                           string='ESOB Settlement', copy=True, readonly=True,
                                           states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})

    def compute_sheet(self):
        employee_id = self.employee_id
        join_date = self.join_date
        op_al_days = self.op_days
        contract_id = self.contract_id
        op_fy_date = datetime(2020, 6, 1).date()
        as_on_date = self.date_to

        # Checking whether contract end date mentioned
        if contract_id.date_end and contract_id.date_end < as_on_date:
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
        # LOP Leaves in Current Period
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
        encashed_amount = 0.00
        objencash = self.env['mbk.encash'].search([('employee_id', '=', employee_id.id), ('state', '!=', 'cancel')])
        for en in objencash:
            encashed_days += en.encash_days
            encashed_amount += en.net_leave_salary

        obj_esob = self.env['mbk.esob'].search([('employee_id', '=', employee_id.id), ('state', '!=', 'cancel')])
        for es in obj_esob:
            if es.id != self.id:
                encashed_days += es.encash_days
                encashed_amount += en.net_leave_salary

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
        #ESOB Days Calculation
        if eligible_days < 365:
            gratuity_days = 0.00
        elif 365 <= eligible_days < 1825:
            gratuity_days = round(eligible_days*21/365, 2)
        else:
            gratuity_days = round(105+((eligible_days-1825)*30/365), 2)
        # Provision Details
        obj_last_leave_p = self.env['mbk.leave_provision.line'].search(
            [('employee_id', '=', employee_id.id), ('leave_provision_id.state', '=', 'posted'),
             ('to_date', '>=', as_on_date)],
            order='to_date', limit=1)
        if obj_last_leave_p:
            self.al_provision_date = obj_last_leave_p.to_date
            self.al_provision_days = obj_last_leave_p.avl_leave_days
            self.al_provision_amount = obj_last_leave_p.avl_leave_amount
        else:
            raise UserError('Leave Provision booking is not found for the employee. Please book provision before settlement')
        obj_last_esob_p = self.env['mbk.esob_provision.line'].search(
            [('employee_id', '=', employee_id.id), ('esob_provision_id.state', '=', 'posted'),
             ('to_date', '=', as_on_date)],
            order='to_date', limit=1)
        if obj_last_esob_p:
            self.esob_provision_date = obj_last_esob_p.to_date
            self.esob_provision_days = obj_last_esob_p.avl_esob_days
            self.esob_provision_amount = obj_last_esob_p.avl_esob_amount
        else:
            raise UserError('ESOB Provision booking is not found for the employee. Please book provision before settlement')

        self.total_days = total_days
        self.eligible_days = eligible_days
        self.lop_days = lop_days
        self.op_days = op_al_days
        self.new_days = new_al_days
        self.leave_taken = c_alt
        self.encashed_days = encashed_days
        self.avl_encash_days = annualleave_days
        self.avl_esob_days = gratuity_days
        self.esob_days = gratuity_days
        self.encash_days = annualleave_days
        self.write({'state': 'verify'})

        return True

    def button_cancel(self):
        self.state = 'cancel'

    def action_esob_cancel(self):
        if self.filtered(lambda slip: slip.state == 'done'):
            raise UserError(_("Cannot cancel a payslip that is done."))
        self.write({'state': 'cancel'})

    def action_esob_draft(self):
        return self.write({'state': 'draft'})

    def action_esob_done(self):
        if self.encash_days <= 0:
            raise UserError('Enter valid Leave Encash Days')

        if self.esob_no == 'New':
            self.esob_no = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(
                'mbk.esob') or _('New')
        return self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        vals['state'] = 'draft'
        res = super(MbkESOB, self).create(vals)
        return res

    def unlink(self):
        for esob in self:
            if esob.state not in ('draft', 'cancel') and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been posted."))
            esob.trans_line.unlink()
        return super(MbkESOB, self).unlink()

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

        esob_name = 'ESOB'
        self.name = '%s - %s - %s' % (esob_name, self.employee_id.name or '', format_date(self.env, self.date_to, date_format="MMMM y"))

        if date_to > al_provision_date:
            self.warning_message = _(
                "This ESOB computation can be erroneous! Provision entries not be generated after %s." %
                (al_provision_date))
        else:
            self.warning_message = False

    @api.depends('encash_days', 'net_salary')
    def compute_encash_amount(self):
        if self.al_provision_days or self.al_provision_days != 0:
            perday_rate = (self.al_provision_amount / self.al_provision_days)
            self.encash_amount = round(perday_rate * self.encash_days, 2)

    @api.depends('esob_days', 'net_salary')
    def compute_esob_amount(self):
        perday_rate = self.basic_salary * 12 / 365
        self.esob_amount = round(perday_rate * self.esob_days, 2)

    @api.depends('encash_amount', 'ticket_amount')
    def compute_net_amount(self):
        self.net_amount = round(self.encash_amount + self.ticket_amount + self.esob_amount, 2)

    def allocate_sheet(self):

        # delete old esob lines
        if self.state in ('draft', 'verify'):
            self.line_ids.unlink()
            obj_payslip = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id), ('state', '!=', 'cancel'),('date', '=', self.date_effective)])
            self.payslip_ids = obj_payslip.ids
        seq = 0
        if len(self.line_ids) == 0:
            new_lines = self.env['mbk.esob.line']
            if self.esob_amount > 0:
                seq += 1
                create_vals = {'esob_id': self.id,
                               'sequence': seq,
                               'type_name': 'ESOB',
                               'type_description': 'Gratuity for '+str(round(self.esob_days, 2))+' days',
                               'amount': self.esob_amount,
                               }
                new_lines.create(create_vals)
            if self.encash_amount>0:
                seq += 1
                create_vals = {'esob_id': self.id,
                               'sequence': seq,
                               'type_name': 'Leave Salary',
                               'type_description': 'Leave Salary for ' + str(round(self.encash_days, 2)) + ' days',
                               'amount': self.encash_amount,
                               }
                new_lines.create(create_vals)

            if self.payslip_ids:
                for pid in self.payslip_ids:
                    ps_amount = 0.00
                    ps_net_amount = 0.00
                    ps_esob_amount = 0.00
                    ps_ded_amount = 0.00
                    ps_period = pid.date_from.strftime("%d-%m-%Y")+' to ' + pid.date_to.strftime("%d-%m-%Y")
                    for pl in pid.line_ids:
                        if pl.code == 'NET':
                            ps_net_amount += pl.amount
                        if pl.code in ('AL', 'ESOB', 'LS'):
                            ps_esob_amount += pl.amount
                        if pl.code in ('PD', 'SA'):
                            ps_ded_amount += pl.amount
                    seq += 1
                    ps_amount = ps_net_amount-(ps_esob_amount+ps_ded_amount)
                    create_vals = {'esob_id': self.id,
                                   'sequence': seq,
                                   'type_name': 'Monthly Salary',
                                   'type_description': 'Monthly Salary for the period ' + ps_period,
                                   'amount': ps_amount,
                                   }
                    new_lines.create(create_vals)
                    if ps_ded_amount != 0.00:
                        seq += 1
                        create_vals = {'esob_id': self.id,
                                       'sequence': seq,
                                       'type_name': 'Deductions',
                                       'type_description': 'Final & Penalty ' + ps_period,
                                       'amount': ps_ded_amount,
                                       }
                        new_lines.create(create_vals)

            return new_lines

class MbkESOBLine(models.Model):
    _name = 'mbk.esob.line'
    _description = 'ESOB Line'
    _order = 'esob_id, sequence'

    esob_id = fields.Many2one('mbk.esob', string='ESOB', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(string='Sl', required=True, index=True, readonly=True, default=10)
    type_name = fields.Char(string='Type', readonly=True, store=True)
    type_description = fields.Char(string='Type', store=True)
    amount = fields.Float(string='Amount', readonly=True, store=True, default=False)