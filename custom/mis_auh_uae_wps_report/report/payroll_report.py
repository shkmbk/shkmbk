from odoo import models, api, _
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from pytz import timezone
import pytz

class MBKPayrollReport(models.AbstractModel):
    _name = 'report.mis_auh_uae_wps_report.payroll_report'
    _description = "Payroll Report"
    
    @api.model
    def _get_employee(self,employee_id):
        if employee_id:
            return ('employee_id', '=', employee_id)
        else:
            return (1, '=', 1)

    def _get_department(self, hr_department_ids):
        if hr_department_ids:
            return ('employee_id.department_id', 'in', hr_department_ids)
        else:
            return (1, '=', 1)

    def _get_analytic(self, analytic_id):
        if analytic_id:
            return ('employee_id.contract_ids.analytic_account_id', '=', analytic_id)
        else:
            return (1, '=', 1)

    def _get_analytic_tags(self,analytic_tag_ids):
        if analytic_tag_ids:
            return ('employee_id.contract_ids.x_analytic_tag_ids', 'in', analytic_tag_ids)
        else:
            return (1, '=', 1)

    def _get_hr_tags(self, category_ids):
        if category_ids:
            return ('employee_id.category_ids', 'in', category_ids)
        else:
            return (1, '=', 1)

    def _get_payment_method(self, payment_method):
        if payment_method:
            return ('employee_id.payment_method', '=', payment_method)
        else:
            return ('company_id', '=', self.env.company.id)
   
    def _get_report_values(self, docids, data=None):
        self.env['ir.rule'].clear_cache()
        start_date_str = data['start_date']
        end_date_str = data['end_date']
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        hr_department_ids = data['hr_department_ids']
        category_ids = data['category_ids']
        analytic_account_id = data['analytic_account_id']
        analytic_tag_ids = data['analytic_tag_ids']
        employee_id = data['employee_id']
        payment_method = data['payment_method']

        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))
        if start_date > end_date:
            raise UserError(_('End date should be greater than or equal to start Date'))

        slips = self.env['hr.payslip'].search([('date_from', '>=', start_date), ('date_to', '<=', end_date), self._get_employee(employee_id), self._get_department(hr_department_ids), self._get_analytic(analytic_account_id),
                                              self._get_analytic_tags(analytic_tag_ids), self._get_hr_tags(category_ids), self._get_payment_method(payment_method)], order="employee_id, number")

        if not slips:
            raise UserError(_('No records found for the selected parameters'))

        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            date = pytz.utc.localize(datetime.now()).astimezone(tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            date = datetime.now()
            time = datetime.now()

        start = str(start_date).split('-')
        end = str(end_date).split('-')
        if start[1] == end[1]:
            report_head = 'THE MONTH ' + end_date.strftime("%B %Y").upper()
            report_footer = 'PVT OFF SALARY - ' + end_date.strftime("%b %Y").upper()
        else:
            report_head = start_date.strftime("%d/%m/%Y").upper() + ' - ' + end_date.strftime(
                "%d/%m/%Y").upper()
            report_footer = start_date.strftime("%m %y").upper() + ' - ' + end_date.strftime("%m %y").upper()
        date_string = end_date.strftime("%B-%y")

        count = 0
        master_table = []

        for rec in slips:
            count += 1
            # CONTRACT SALARY (BASIC + ALLOWANCE)
            contract_salary = rec.employee_id.contract_id.wage + rec.employee_id.contract_id.x_house_rent + rec.employee_id.contract_id.x_transport + rec.employee_id.contract_id.x_other_allowance + rec.employee_id.contract_id.x_fixed_ot
                 # DAYS
            worked_days = 0.0
            for w_line in rec.worked_days_line_ids:
                if w_line.work_entry_type_id.id == 1:
                    worked_days = -w_line.number_of_days if rec.credit_note else w_line.number_of_days
            amount_basic = 0.0
            amount_allow = 0.00
            amount_fot = 0.00
            amount_ls = 0.00
            amount_at = 0.00
            amount_esob = 0.00
            amount_gross = 0.00
            amount_fine = 0.00
            amount_adv = 0.00
            amount_net = 0.00
            for line in rec.line_ids:
                if line.code == 'BASIC':
                    amount_basic = -line.total if rec.credit_note else line.total
                if line.code == 'ALW':
                    amount_allow = -line.total if rec.credit_note else line.total
                if line.code == 'FOT':
                    amount_fot = -line.total if rec.credit_note else line.total
                if line.code == 'LS':
                    amount_ls = -line.total if rec.credit_note else line.total
                if line.code == 'AT':
                    amount_at = -line.total if rec.credit_note else line.total
                if line.code == 'ESOB':
                    amount_esob = -line.total if rec.credit_note else line.total
                if line.code == 'GROSS':
                    amount_gross = -line.total if rec.credit_note else line.total
                if line.code == 'PD':
                    amount_fine = -line.total if rec.credit_note else line.total
                if line.code == 'SA':
                    amount_adv = -line.total if rec.credit_note else line.total
                if line.code == 'NET':
                    amount_net = -line.total if rec.credit_note else line.total

            master_table.append({
                            'sl_no': count,
                            'emp_name': rec.employee_id.name,
                            'emp_code': rec.employee_id.registration_number,
                            'designation': rec.employee_id.job_id.name,
                            'division':  rec.employee_id.contract_id.analytic_account_id.name,
                            'department':  rec.employee_id.department_id.name,
                            'payment_mode': rec.employee_id.payment_method.name,
                            'Period': rec.date_to.strftime("%b %y"),
                            'contract_salary': contract_salary,
                            'worked_days': worked_days,
                            'amount_basic': amount_basic,
                            'amount_allow': amount_allow,
                            'amount_fot': amount_fot,
                            'amount_ls': amount_ls,
                            'amount_at': amount_at,
                            'amount_esob': amount_esob,
                            'amount_gross': amount_gross,
                            'amount_fine': amount_fine,
                            'amount_adv': amount_adv,
                            'amount_net': amount_net,
                        })
        # master_table.sort(key=lambda g:(g['annualleave_amount'],g['eligible_days']), reverse=True)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.employee',
            'docs': master_table,
            'report_head': report_head,
        }
        return docargs