from odoo import models, fields, api
from datetime import date
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import format_date


class MbkLeaveProvision(models.Model):
    _name = 'mbk.leave_provision'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Employee Leave Provision Booking'
    _order = 'date_to desc'

    name = fields.Char(string='Name', readonly=True, store=True, default='New')
    date = fields.Date('Date', default=fields.Date.to_string(date.today()),
                       states={'draft': [('readonly', False)], 'verify': [('readonly', False)]}, readonly=True,
                       help="Keep empty to use the period of the validation(Payslip) date.")
    ref = fields.Char(string='Reference', readonly=True, copy=False,
                      states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    date_to = fields.Date(string='As on Date', readonly=True, required=True,
                          states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', readonly=True,
                                          states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True,
                                  states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=1)
    journal_id = fields.Many2one('account.journal', string='Journal', default=101, tracking=True, readonly=True,
                                 states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, tracking=True, default='draft')
    note = fields.Text(string='Internal Note', readonly=True,
                       states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    amount = fields.Float(string='Total Amount', readonly=True, store=True, default=False)

    warning_message = fields.Char(readonly=True)
    line_ids = fields.One2many('mbk.leave_provision.line', 'leave_provision_id',
                               string='Leave Provision Booking', copy=True, readonly=True,
                               states={'draft': [('readonly', False)]})
    account_move_id = fields.Many2one('account.move', 'Journal Entries')

    @api.model
    def _get_employee(self, employee_id):
        if employee_id:
            return ('employee_id', '=', employee_id)
        else:
            return (1, '=', 1)

    @api.model
    def _get_analytic(self, analytic_id):
        if analytic_id:
            return ('analytic_account_id', '=', analytic_id)
        else:
            return (1, '=', 1)

    def action_load_sheet(self):
        employee_id = self.employee_id
        analytic_account_id = self.analytic_account_id
        as_on_date = self.date_to
        # as_on_date_str = datetime.strptime(date_to, '%Y-%m-%d').date()
        op_fy_date = datetime(2020, 6, 1).date()

        if not self.ref:
            self.ref = 'Leave Provision as on ' + (self.date_to).strftime("%d-%m-%Y")
        # delete old leave provision lines
        if self.state in ('draft'):
            self.line_ids.unlink()

        obj_emp = self.env['hr.contract'].search(
            [('state', '=', 'open'), ('employee_id.date_of_join', '<=', as_on_date),
             self._get_analytic(analytic_account_id.id),
             self._get_employee(employee_id.id)])
        if not obj_emp:
            raise UserError('There are no Employee found for selected parameters')
        new_lines = self.env['mbk.leave_provision.line']

        sl_no = 0
        total_amount = 0.00
        for rec in obj_emp:
            join_date = rec.employee_id.date_of_join
            contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id), ('date_start', '<=', as_on_date), ('date_end', '>=', as_on_date)])
            if contract:
                basic_salary = contract.wage
                allowances = contract.x_other_allowance
                contract_id = contract.id
            else:
                basic_salary = rec.wage
                allowances = rec.x_other_allowance
                contract_id = rec.id

            net_salary = basic_salary+allowances
            per_day = net_salary*12/365

            # Checking weather contract end date mentioned
            if rec.date_end and as_on_date > rec.date_end:
                to_date = rec.date_end
            else:
                to_date = as_on_date

            total_days = (to_date - join_date).days + 1
            op_eligible_days = rec.employee_id.op_eligible_days
            op_al_days = rec.employee_id.op_leave_days
            cumulative_provision_booked = 0.0
            cumulative_days_booked = 0.00
            cumulative_eligible_days = 0.00
            obj_last_leave_p = self.env['mbk.leave_provision.line'].search(
                [('employee_id', '=', rec.employee_id.id), ('leave_provision_id.state', '=', 'posted')],
                order='to_date desc', limit=1)
            last_leave_pb = obj_last_leave_p.to_date
            if not last_leave_pb:
                cumulative_provision_booked = 0.0
                cumulative_days_booked = 0.00
                cumulative_eligible_days = 0.00
                cumulative_total_days = 0.00
                cumulative_lop_days = 0.00
            else:
                cumulative_provision_booked = obj_last_leave_p.avl_leave_amount
                cumulative_eligible_days = obj_last_leave_p.eligible_days
                cumulative_total_days = obj_last_leave_p.total_days
                cumulative_lop_days = obj_last_leave_p.lop_days

            if join_date < op_fy_date:
                op_lop_days = (op_fy_date - join_date).days - op_eligible_days
                c_total_days = (to_date - op_fy_date).days + 1
            else:
                op_lop_days = 0
                c_total_days = (to_date - join_date).days + 1

            objlopleave = self.env['hr.leave'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'validate'),
                 ('holiday_status_id.unpaid', '=', 1), ('request_date_from', '<=', to_date)])
            c_lop = 0.00
            for lop in objlopleave:
                if lop.request_date_to <= to_date:
                    c_lop += lop.number_of_days
                else:
                    c_lop += (to_date - lop.request_date_from).days + 1

            lop_days = op_lop_days + c_lop

            if join_date < op_fy_date:
                eligible_days = op_eligible_days + c_total_days - c_lop
            else:
                eligible_days = c_total_days - c_lop
            # Annual Leave Taken
            objalleave = self.env['hr.leave'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'validate'), ('holiday_status_id', '=', 1),
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
            objencash = self.env['mbk.encash'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'done'), ('date_to', '<=', to_date)])

            for en in objencash:
                if en.encash_days:
                    encashed_days += en.encash_days
                    encashed_amount += en.net_leave_salary

            obj_esob = self.env['mbk.esob'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '!=', 'cancel'), ('date_to', '<=', to_date)])
            for es in obj_esob:
                encashed_days += es.encash_days
                encashed_amount += es.encash_amount

            total_leaves = encashed_days + c_alt

            # Computing total booked Leave Salary provision
            obj_ls_provision = self.env['mbk.leave_provision.line'].search(
                [('employee_id', '=', rec.employee_id.id), ('leave_provision_id.state', '=', 'posted'), ('to_date', '<=', to_date)])
            lsp_booked = 0.00
            for lsp in obj_ls_provision:
                lsp_booked += lsp.amount
                cumulative_days_booked += lsp.booking_leave_days

            c_eligible_days = c_total_days - c_lop
            new_al_days = (c_eligible_days * 30 / 365)
            total_al_days = round(op_al_days + new_al_days, 2)
            booking_total_days = total_days - cumulative_total_days
            booking_eligible_days = eligible_days - cumulative_eligible_days
            booking_lop_days = lop_days - cumulative_lop_days
            booking_leave_days = round(total_al_days-cumulative_days_booked, 2)
            amount = round(per_day * booking_leave_days, 2)
            annualleave_days = round(op_al_days + new_al_days - total_leaves, 2)
            annualleave_amount = lsp_booked + amount - encashed_amount

            total_amount += amount
            if amount > 0:
                sl_no += 1
                values = {
                    'leave_provision_id': self.id,
                    'sl_no': sl_no,
                    'employee_code': rec.employee_id.registration_number,
                    'employee_id': rec.employee_id.id,
                    'to_date': to_date,
                    'amount': amount,
                    'join_date': join_date,
                    'net_salary': net_salary,
                    'booking_total_days': booking_total_days,
                    'booking_eligible_days': booking_eligible_days,
                    'booking_lop_days': booking_lop_days,
                    'booking_leave_days': booking_leave_days,
                    'last_booking_date': last_leave_pb,
                    'total_days': total_days,
                    'lop_days': lop_days,
                    'eligible_days': eligible_days,
                    'avl_leave_days': annualleave_days,
                    'avl_leave_amount': annualleave_amount,
                    'contract_id': contract_id
                }
                new_lines.create(values)
        self.amount = total_amount
        return new_lines

    def button_cancel(self):
        self.state = 'cancel'

    def action_leave_cancel(self):
        if self.filtered(lambda slip: slip.state == 'post'):
            raise UserError(_("Cannot cancel a Provision that is post."))
        self.write({'state': 'cancel'})

    def action_leave_draft(self):
        return self.write({'state': 'draft'})

    def action_post(self):
        if not self.account_move_id and len(self.line_ids) > 0:
            isheader = True
            total_amount = self.amount
            move_line_vals = []
            master_table = []
            line_ids = []

            for rec in self.line_ids:
                master_table.append({
                    'analytic_account_id': rec.contract_id.analytic_account_id.id,
                    'analytic_tag_ids': rec.contract_id.x_analytic_tag_ids.ids,
                    'amount': rec.amount,
                })

            for line in master_table:
                existing_lines = (
                    line_id for line_id in line_ids
                    if line_id['analytic_account_id'] == (line['analytic_account_id'])
                    and line_id['analytic_tag_ids'] == line['analytic_tag_ids']
                )

                provision_line = next(existing_lines, False)
                if not provision_line:
                    #raise UserError(line.get('analytic_account_id'))
                    provision_line = {
                        'analytic_account_id': line.get('analytic_account_id'),
                        'analytic_tag_ids': line.get('analytic_tag_ids'),
                        'amount': line.get('amount'),
                    }
                    line_ids.append(provision_line)
                else:
                    provision_line['amount'] += line['amount']

            for rec in line_ids:
                create_vals = (0, 0, {'name': self.ref,
                                      'date': self.date,
                                      'ref': 'Leave Provision as on ' + str(self.date_to),
                                      'parent_state': 'draft',
                                      'company_id': self.company_id.id,
                                      'account_id': self.journal_id.default_debit_account_id.id,
                                      'quantity': 1,
                                      'analytic_account_id': rec['analytic_account_id'],
                                      'analytic_tag_ids': rec['analytic_tag_ids'],
                                      'debit': rec['amount'],
                                      'credit': 0.0,
                                      })
                move_line_vals.append(create_vals)
                create_vals = (0, 0, {'name': self.ref,
                                      'date': self.date,
                                      'ref': 'Leave Provision as on ' + (self.date_to).strftime("%d-%m-%Y"),
                                      'parent_state': 'draft',
                                      'company_id': self.company_id.id,
                                      'account_id': self.journal_id.default_credit_account_id.id,
                                      'quantity': 1,
                                      'analytic_account_id': rec['analytic_account_id'],
                                      'analytic_tag_ids': rec['analytic_tag_ids'],
                                      'debit': 0,
                                      'credit': rec['amount'],
                                      })
                move_line_vals.append(create_vals)
            if isheader:
                move_vals = {'date': self.date,
                             'journal_id': self.journal_id.id,
                             'ref': self.ref,
                             'name': '/',
                             'company_id': self.company_id.id,
                             'state': 'draft',
                             'type': 'entry',
                             'amount_total': total_amount,
                             'line_ids': move_line_vals,
                             }
                obj_ac_move = self.env['account.move'].create(move_vals)
                obj_ac_move.post()
                self.account_move_id = obj_ac_move.id
            if self.name == 'New':
                self.name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(
                    'mbk.leave_provision') or _('New')
            return self.write({'state': 'posted'})

    @api.model
    def create(self, vals):
        vals['state'] = 'draft'
        res = super(MbkLeaveProvision, self).create(vals)
        return res

    def unlink(self):
        for leave in self:
            if leave.state not in ('draft') and not self._context.get('force_delete'):
                raise UserError("You cannot delete an entry which has been posted.")
            leave.trans_line.unlink()
        return super(MbkLeaveProvision, self).unlink()


class MbkLeaveProvisionLine(models.Model):
    _name = 'mbk.leave_provision.line'
    _description = 'Leave Provision Line'
    _order = 'leave_provision_id, sl_no'

    leave_provision_id = fields.Many2one('mbk.leave_provision', string='Leave Provision', required=True,
                                        ondelete='cascade', index=True)
    sl_no = fields.Integer(string='Sl', required=True, index=True, readonly=True, default=10)
    employee_code = fields.Char(string='Code', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True,
                                  states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True, readonly=True,
                                  states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})
    to_date = fields.Date(string='As on Date', readonly=True, store=True)
    amount = fields.Float(string='Amount', readonly=True, store=True, default=False)
    join_date = fields.Date(string='Date Of Join', readonly=True, store=True, default=False)
    net_salary = fields.Float(string='Net Salary', readonly=True, store=True, default=False)
    last_booking_date = fields.Date('Last Booking Date', readonly=True, store=True)
    booking_total_days = fields.Float(string='Current Days', readonly=True, store=True, default=False)
    booking_eligible_days = fields.Float(string='Current Eligible Days', readonly=True, store=True, default=False)
    booking_lop_days = fields.Float(string='Current LOP Days', readonly=True, store=True, default=False)
    booking_leave_days = fields.Float(string='Current Leave Days', readonly=True, store=True, default=False)
    c_lop_days = fields.Float(string='Current LOP Days', readonly=True, store=True, default=False)
    total_days = fields.Float(string='Total Days', readonly=True, store=True, default=False)
    lop_days = fields.Float(string='LOP Days', readonly=True, store=True, default=False)
    eligible_days = fields.Float(string='Total Eligible Days', readonly=True, default=False)
    avl_leave_days = fields.Float(string='Balance Leave Days', readonly=True, store=True, default=False)
    avl_leave_amount = fields.Float(string='Balance Leave Amount', readonly=True, compute='compute_leave_amount', store=True,
                                   default=False)
    remarks = fields.Char(string='Remarks', store=True)
