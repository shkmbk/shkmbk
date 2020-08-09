import base64
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval


class MisHrPayslip(models.Model):
    _inherit = 'hr.payslip'

    paid_allowance = fields.Monetary(compute='_compute_allowance')

    def _compute_allowance(self):
        contract = self.contract_id
        allowance_amount = contract.x_house_rent
        unpaid_work_entry_types = self.struct_id.unpaid_work_entry_type_ids


        work_hours = contract._get_work_hours(self.date_from, self.date_to)
        total_hours = sum(work_hours.values()) or 1

        for payslip in self:
            self.ensure_one()
            if not self.worked_days_line_ids:
                return allowance_amount
            total_allowance = 0
            is_unpaid = False
            for line in self.worked_days_line_ids:
                is_unpaid = line.work_entry_type_id in unpaid_work_entry_types
                total_allowance += line.number_of_hours * allowance_amount / total_hours if is_unpaid else 0
            payslip.paid_allowance = allowance_amount-total_allowance

    def _get_paid_amount(self):
        self.ensure_one()
        if not self.worked_days_line_ids:
            return self._get_contract_wage()
        total_amount = 0
        for line in self.worked_days_line_ids:
            total_amount += line.amount
        return total_amount


