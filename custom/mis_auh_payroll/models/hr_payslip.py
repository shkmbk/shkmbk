import base64
from datetime import date, datetime
from datetime import timedelta
import calendar
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval
from odoo.tools import float_compare, float_is_zero

class MisHrPayslip(models.Model):
    _inherit = 'hr.payslip'

    paid_allowance = fields.Monetary(compute='_compute_allowance')
    paid_fot=fields.Monetary(compute='_compute_fot')


    def _compute_allowance(self):
        contract = self.contract_id
        allowance_amount = contract.x_other_allowance
        unpaid_work_entry_types = self.struct_id.unpaid_work_entry_type_ids
        stdate=self.date_from
        startmonth=stdate.month
        startyear = stdate.year

        mstartdate=datetime(startyear, startmonth , 1)
        end_date = mstartdate +  relativedelta(months=1)
        end_date = end_date + relativedelta(days=-1)        


        work_hours = contract._get_work_hours(self.date_from, self.date_to)
        work_hours_in_this_month = contract._get_work_hours(mstartdate, end_date)
        total_hours = sum(work_hours.values()) or 1
        total_work_hours_in_this_month = sum(work_hours_in_this_month.values()) or 1

        for payslip in self:
            self.ensure_one()
            if not self.worked_days_line_ids:
                return allowance_amount
            total_allowance = 0
            is_paid = False
            for line in self.worked_days_line_ids:
                #is_unpaid = line.work_entry_type_id in unpaid_work_entry_types
                is_paid = line.work_entry_type_id not in unpaid_work_entry_types
                total_allowance += line.number_of_hours * allowance_amount / total_work_hours_in_this_month if is_paid else 0
            payslip.paid_allowance = total_allowance
            
    def _compute_fot(self):
        contract = self.contract_id
        fot_amount = contract.x_fixed_ot
        unpaid_work_entry_types = self.struct_id.unpaid_work_entry_type_ids
        stdate=self.date_from
        startmonth=stdate.month
        startyear = stdate.year

        mstartdate=datetime(startyear, startmonth , 1)
        end_date = mstartdate +  relativedelta(months=1)
        end_date = end_date + relativedelta(days=-1)        
        
        
        work_hours = contract._get_work_hours(self.date_from, self.date_to)
        work_hours_in_this_month = contract._get_work_hours(mstartdate, end_date)
        total_hours = sum(work_hours.values()) or 1
        total_work_hours_in_this_month = sum(work_hours_in_this_month.values()) or 1

        for payslip in self:
            self.ensure_one()
            if not self.worked_days_line_ids:
                return fot_amount
            total_fot = 0
            #is_unpaid = False
            is_paid = False
            for line in self.worked_days_line_ids:
                #is_unpaid = line.work_entry_type_id in unpaid_work_entry_types
                is_paid = line.work_entry_type_id not in unpaid_work_entry_types
                total_fot+= line.number_of_hours * fot_amount / total_work_hours_in_this_month if is_paid else 0
            payslip.paid_fot = total_fot

    def _get_paid_amount(self):
        self.ensure_one()
        if not self.worked_days_line_ids:
            return self._get_contract_wage()
        total_amount = 0
        for line in self.worked_days_line_ids:
            total_amount += line.amount
        return total_amount

    def _get_worked_day_lines(self):
        """
        :returns: a list of dict containing the worked days values that should be applied for the given payslip
        """
        res = []
        # fill only if the contract as a working schedule linked
        self.ensure_one()
        contract = self.contract_id
        if contract.resource_calendar_id:
            paid_amount = self._get_contract_wage()
            unpaid_work_entry_types = self.struct_id.unpaid_work_entry_type_ids.ids
            stdate=self.date_from
            startmonth=stdate.month
            startyear = stdate.year

            mstartdate=datetime(startyear, startmonth , 1)

            end_date = mstartdate +  relativedelta(months=1)
            end_date = end_date + relativedelta(days=-1)

            #raise UserError(end_date)

            work_hours = contract._get_work_hours(self.date_from, self.date_to)
            work_hours_in_this_month = contract._get_work_hours(mstartdate, end_date)

            total_hours = sum(work_hours.values()) or 1
            work_hours_in_this_month = sum(work_hours_in_this_month.values()) or 1
            work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
            biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
            #raise UserError(biggest_work)
            add_days_rounding = 0
            for work_entry_type_id, hours in work_hours_ordered:
                work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
                is_paid = work_entry_type_id not in unpaid_work_entry_types
                calendar = contract.resource_calendar_id
                days = round(hours / calendar.hours_per_day, 5) if calendar.hours_per_day else 0
                if work_entry_type_id == biggest_work:
                    days += add_days_rounding
                day_rounded = self._round_days(work_entry_type, days)
                add_days_rounding += (days - day_rounded)
                attendance_line = {
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type_id,
                    'number_of_days': day_rounded,
                    'number_of_hours': hours,
                    'amount': hours * paid_amount / work_hours_in_this_month if is_paid else 0,
                }
                res.append(attendance_line)
        return res

    def action_payslip_done(self):

        """
            Generate the accounting entries related to the selected payslips
            A move is created for each journal and for each month.
        """
        res = super(MisHrPayslip, self).action_payslip_done()
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = {
            slip.struct_id.journal_id.id: {fields.Date().end_of(slip.date_to, 'month'): self.env['hr.payslip']} for slip
            in payslips_to_post}
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip

        for journal_id in slip_mapped_data:  # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]:  # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip_date
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': date,
                }

                for slip in slip_mapped_data[journal_id][slip_date]:
                    move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name or ''
                    move_dict['narration'] += '\n'
                    for line in slip.line_ids.filtered(lambda line: line.category_id):
                        amount = -line.total if slip.credit_note else line.total
                        if line.code == 'NET':  # Check if the line is the 'Net Salary'.
                            for tmp_line in slip.line_ids.filtered(lambda line: line.category_id):
                                if tmp_line.salary_rule_id.not_computed_in_net:  # Check if the rule must be computed in the 'Net Salary' or not.
                                    if amount > 0:
                                        amount -= abs(tmp_line.total)
                                    elif amount < 0:
                                        amount += abs(tmp_line.total)
                        if float_is_zero(amount, precision_digits=precision):
                            continue
                        debit_account_id = line.salary_rule_id.account_debit.id
                        credit_account_id = line.salary_rule_id.account_credit.id

                        if debit_account_id:  # If the rule has a debit account.
                            debit = amount if amount > 0.0 else 0.0
                            credit = -amount if amount < 0.0 else 0.0

                            existing_debit_lines = (
                                line_id for line_id in line_ids if
                                line_id['name'] == line.name
                                and line_id['account_id'] == debit_account_id
                                and line_id['analytic_account_id'] == (
                                            line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id)
                                and line_id['analytic_tag_ids'] == (
                                        slip.contract_id.x_analytic_tag_ids.ids)
                                and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)))
                            debit_line = next(existing_debit_lines, False)

                            if not debit_line:
                                debit_line = {
                                    'name': line.name,
                                    'partner_id': False,
                                    'account_id': debit_account_id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id,
                                    'analytic_tag_ids': slip.contract_id.x_analytic_tag_ids.ids,
                                }
                                line_ids.append(debit_line)
                            else:
                                debit_line['debit'] += debit
                                debit_line['credit'] += credit

                        if credit_account_id:  # If the rule has a credit account.
                            debit = -amount if amount < 0.0 else 0.0
                            credit = amount if amount > 0.0 else 0.0
                            existing_credit_line = (
                                line_id for line_id in line_ids if
                                line_id['name'] == line.name
                                and line_id['account_id'] == credit_account_id
                                and line_id['analytic_account_id'] == (
                                            line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id)
                                and line_id['analytic_tag_ids'] == (
                                        slip.contract_id.x_analytic_tag_ids.ids)
                                and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0))
                            )
                            credit_line = next(existing_credit_line, False)

                            if not credit_line:
                                credit_line = {
                                    'name': line.name,
                                    'partner_id': False,
                                    'account_id': credit_account_id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id,
                                    'analytic_tag_ids': slip.contract_id.x_analytic_tag_ids.ids,
                                }
                                line_ids.append(credit_line)
                            else:
                                credit_line['debit'] += debit
                                credit_line['credit'] += credit

                for line_id in line_ids:  # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']

                # The code below is called if there is an error in the balance between credit and debit sum.
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_credit_account_id.id
                    if not acc_id:
                        raise UserError(
                            _('The Expense Journal "%s" has not properly configured the Credit Account!') % (
                                slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_credit = next(existing_adjustment_line, False)

                    if not adjust_credit:
                        adjust_credit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': 0.0,
                            'credit': debit_sum - credit_sum,
                        }
                        line_ids.append(adjust_credit)
                    else:
                        adjust_credit['credit'] = debit_sum - credit_sum

                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_debit_account_id.id
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (
                            slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_debit = next(existing_adjustment_line, False)

                    if not adjust_debit:
                        adjust_debit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': credit_sum - debit_sum,
                            'credit': 0.0,
                        }
                        line_ids.append(adjust_debit)
                    else:
                        adjust_debit['debit'] = credit_sum - debit_sum

                # Add accounting lines in the move
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move = self.env['account.move'].create(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'move_id': move.id, 'date': date})
        return res


