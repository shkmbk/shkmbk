# -*- coding: utf-8 -*-
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo.tools import date_utils
import xlsxwriter
import base64
from odoo import fields, models, api, _
from io import BytesIO
from pytz import timezone
import pytz


class Mbkannualleave_Wizard(models.TransientModel):
    _name = 'mbk.wizard.report.annualleave'
    _description = "Annual Leave Report"

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))

    @api.model
    def _get_employee(self, employee_id):
        if employee_id:
            return ('employee_id', '=', employee_id)
        else:
            return (1, '=', 1)

    def _get_department(self, hr_department_ids):
        if hr_department_ids:
            return ('department_id', 'in', hr_department_ids)
        else:
            return (1, '=', 1)

    def _get_analytic(self, analytic_id):
        if analytic_id:
            return ('analytic_account_id', '=', analytic_id)
        else:
            return (1, '=', 1)

    def _get_analytic_tags(self, analytic_tag_ids):
        if analytic_tag_ids:
            return ('x_analytic_tag_ids', 'in', analytic_tag_ids)
        else:
            return (1, '=', 1)

    ason_date = fields.Date(default=fields.Date.to_string(date.today()), string='As On Date', required=True)
    employee_id = fields.Many2one('hr.employee', "Employee")
    hr_department_ids = fields.Many2many('hr.department', string='Department(s)')
    category_ids = fields.Many2many('hr.employee.category', string='Tags')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)

    def print_annualleave_report_pdf(self):
        data = {}
        data['ason_date'] = self.ason_date
        data['employee_id'] = self.employee_id.id
        tmpdate = self.ason_date
        data['hr_department_ids'] = self.hr_department_ids.ids
        data['category_ids'] = self.category_ids.ids
        data['analytic_account_id'] = self.analytic_account_id.id
        data['analytic_tag_ids'] = self.analytic_tag_ids.ids
        data['header_date'] = tmpdate.strftime("%d-%m-%Y")
        report = self.env.ref('mbk_reports.annualleave_report_pdf')
        return report.report_action(self, data=data)

    def print_annualleave_report_xls(self):
        self.env['ir.rule'].clear_cache()
        as_on_date = self.ason_date
        employee_id = self.employee_id
        hr_department_ids = self.hr_department_ids.ids
        category_ids = self.category_ids.ids
        analytic_account_id = self.analytic_account_id.id
        analytic_tag_ids = self.analytic_tag_ids.ids
        header_date = as_on_date.strftime("%d-%m-%Y")

        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))

        obj_emp = self.env['hr.contract'].search(
            [('state', 'in', ['open', 'close']), ('employee_id.date_of_join', '<=', as_on_date),
             self._get_analytic(analytic_account_id),
             self._get_department(hr_department_ids), self._get_analytic_tags(analytic_tag_ids),
             self._get_employee(employee_id)])

        if not obj_emp:
            raise UserError('There are no employee found for selected parameters')

        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            c_date = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            c_date = datetime.now()

        dt_string = as_on_date.strftime("%d/%m/%Y")
        report_name = 'Annual_Leave_Report_'
        filename = report_name + c_date.strftime("%y%m%d%H%M%S")

        op_fy_date = datetime(2020, 6, 1)

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf = {}

        wbf['content'] = workbook.add_format()
        wbf['header'] = workbook.add_format({'bold': 1, 'align': 'center'})
        wbf['content_float'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
        wbf['content_border'] = workbook.add_format()
        wbf['content_border'].set_top()
        wbf['content_border'].set_bottom()
        wbf['content_border'].set_left()
        wbf['content_border'].set_right()

        wbf['content_float_border'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
        wbf['content_float_border'].set_top()
        wbf['content_float_border'].set_bottom()
        wbf['content_float_border'].set_left()
        wbf['content_float_border'].set_right()

        wbf['content_date_border'] = workbook.add_format({'align': 'center', 'num_format': 'dd/mm/yyyy'})
        wbf['content_date_border'].set_top()
        wbf['content_date_border'].set_bottom()
        wbf['content_date_border'].set_left()
        wbf['content_date_border'].set_right()

        wbf['content_border_bg_total'] = workbook.add_format({'align': 'right', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_border_bg_total'].set_top()
        wbf['content_border_bg_total'].set_bottom()
        wbf['content_border_bg_total'].set_left()
        wbf['content_border_bg_total'].set_right()

        wbf['content_border_bg'] = workbook.add_format({'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_border_bg'].set_top()
        wbf['content_border_bg'].set_bottom()
        wbf['content_border_bg'].set_left()
        wbf['content_border_bg'].set_right()

        wbf['content_float_border_bg'] = workbook.add_format(
            {'align': 'right', 'num_format': '#,##0.00', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_float_border_bg'].set_top()
        wbf['content_float_border_bg'].set_bottom()
        wbf['content_float_border_bg'].set_left()
        wbf['content_float_border_bg'].set_right()

        wbf['content_border_bg_c'] = workbook.add_format({'align': 'center', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_border_bg_c'].set_top()
        wbf['content_border_bg_c'].set_bottom()
        wbf['content_border_bg_c'].set_left()
        wbf['content_border_bg_c'].set_right()

        worksheet = workbook.add_worksheet("Annual Leave Report")

        count = 0

        # Report Heading
        worksheet.merge_range('A%s:P%s' % (1, 1), 'ANNUAL LEAVE REPORT AS ON ' + dt_string, wbf['header'])
        count += 1
        col = 0
        worksheet.set_column(col, col, 6)
        worksheet.write(count, col, 'Sl. No.', wbf['content_border_bg_c'])
        col += 1
        worksheet.set_column(col, col, 40)
        worksheet.write(count, col, 'Employee', wbf['content_border_bg_c'])
        col += 1
        worksheet.set_column(col, col, 8)
        worksheet.write(count, col, 'Code', wbf['content_border_bg_c'])
        col += 1
        worksheet.set_column(col, col, 10)
        worksheet.write(count, col, 'Join Date', wbf['content_border_bg_c'])
        col += 1
        worksheet.set_column(col, col, 12)
        worksheet.write(count, col, 'Net Salary', wbf['content_border_bg_c'])
        col += 1
        worksheet.set_column(col, col, 12)
        worksheet.write(count, col, 'Total Days', wbf['content_border_bg'])
        col += 1
        worksheet.set_column(col, col, 12)
        worksheet.write(count, col, 'LOP Days', wbf['content_border_bg'])
        col += 1
        worksheet.set_column(col, col, 12)
        worksheet.write(count, col, 'Eligible Days', wbf['content_border_bg_c'])
        col += 1
        worksheet.set_column(col, col, 12)
        worksheet.write(count, col, 'Opening Days', wbf['content_border_bg'])
        col += 1
        worksheet.set_column(col, col, 12)
        worksheet.write(count, col, 'New Days', wbf['content_border_bg'])
        col += 1
        worksheet.set_column(col, col, 12)
        worksheet.write(count, col, 'Leave Taken', wbf['content_border_bg'])
        col += 1
        worksheet.set_column(col, col, 12)
        worksheet.write(count, col, 'Encash', wbf['content_border_bg_c'])
        col += 1
        worksheet.set_column(col, col, 12)
        worksheet.write(count, col, 'Balance Days', wbf['content_border_bg'])
        col += 1
        worksheet.set_column(col, col, 15)
        worksheet.write(count, col, 'Balance Amount', wbf['content_border_bg'])
        col += 1
        worksheet.set_column(col, col, 14)
        worksheet.write(count, col, 'Provision Date', wbf['content_border_bg'])
        col += 1
        worksheet.set_column(col, col, 16.5)
        worksheet.write(count, col, 'Provision Amount', wbf['content_border_bg'])

        op_fy_date = datetime(2020, 6, 1).date()

        for rec in obj_emp:
            join_date = rec.employee_id.date_of_join
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', rec.employee_id.id), ('date_start', '<=', as_on_date),
                 ('date_end', '>=', as_on_date)])
            if contract:
                basic_salary = contract.wage
                allowances = contract.x_other_allowance
            else:
                basic_salary = rec.wage
                allowances = rec.x_other_allowance

            net_salary = basic_salary + allowances
            per_day = net_salary * 12 / 365
            op_al_days = rec.employee_id.op_leave_days

            # Checking whether contract end date mentioned
            if rec.date_end:
                to_date = rec.date_end
            else:
                to_date = as_on_date

            total_days = (to_date - join_date).days + 1
            op_eligible_days = rec.employee_id.op_eligible_days

            if join_date < op_fy_date:
                op_lop_days = (op_fy_date - join_date).days - op_eligible_days
                c_total_days = (to_date - op_fy_date).days + 1
            else:
                op_lop_days = 0
                c_total_days = (to_date - join_date).days + 1

            # LOP Leaves in Current Period
            objlopleave = self.env['hr.leave'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'validate'),
                 ('holiday_status_id.unpaid', '=', 1), ('request_date_from', '<=', to_date)])
            c_lop = 0.00
            for lop in objlopleave:
                if lop.request_date_to <= to_date:
                    c_lop += lop.number_of_days
                else:
                    c_lop += (to_date - lop.request_date_from).days + 1
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
                    encashed_amount += en.encash_amount

            obj_esob = self.env['mbk.esob'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '!=', 'cancel'), ('date_to', '<=', to_date)])
            for es in obj_esob:
                encashed_days += es.encash_days
                encashed_amount += es.encash_amount

            total_leaves = encashed_days + c_alt
            lop_days = op_lop_days + c_lop

            if join_date < op_fy_date:
                eligible_days = op_eligible_days + c_total_days - c_lop
            else:
                eligible_days = c_total_days - c_lop
            c_eligible_days = c_total_days - c_lop

            new_al_days = (c_eligible_days * 30 / 365)
            annualleave_days = round(op_al_days + new_al_days - total_leaves, 2)
            annualleave_amount = round(per_day * annualleave_days, 2)

            obj_last_leave_p = self.env['mbk.leave_provision.line'].search(
                [('employee_id', '=', rec.employee_id.id), ('leave_provision_id.state', '=', 'posted'),
                 ('to_date', '<=', as_on_date)],
                order='to_date desc', limit=1)

            last_leave_pb_date = obj_last_leave_p.to_date
            provision_bal_amount = obj_last_leave_p.avl_leave_amount

            if last_leave_pb_date:
                last_leave_pb_date_str = last_leave_pb_date.strftime("%d-%m-%Y")
            else:
                last_leave_pb_date_str = False

            # Computing total booked Leave Salary provision
            obj_ls_provision = self.env['mbk.leave_provision.line'].search(
                [('employee_id', '=', rec.employee_id.id), ('leave_provision_id.state', '=', 'posted'),
                 ('to_date', '<=', as_on_date)])
            lsp_booked = 0.00
            for lsp in obj_ls_provision:
                lsp_booked += lsp.amount

            net_leave_amount = lsp_booked - encashed_amount

            count += 1
            col = 0

            # SEQ
            worksheet.write(count, col, count - 2, wbf['content_border'])

            # Employee
            col += 1
            worksheet.write(count, col, rec.employee_id.name, wbf['content_border'])

            # Code
            col += 1
            worksheet.write(count, col, rec.employee_id.registration_number, wbf['content_border'])
            # Join Date
            col += 1
            worksheet.write(count, col, join_date, wbf['content_date_border'])
            # Net Salary
            col += 1
            worksheet.write(count, col, net_salary, wbf['content_float_border'])
            # Total Days
            col += 1
            worksheet.write(count, col, total_days, wbf['content_float_border'])
            # LOP Days
            col += 1
            worksheet.write(count, col, lop_days, wbf['content_float_border'])
            # Eligible Days
            col += 1
            worksheet.write(count, col, eligible_days, wbf['content_float_border'])
            # Opening Days
            col += 1
            worksheet.write(count, col, op_al_days, wbf['content_float_border'])
            # New Days
            col += 1
            worksheet.write(count, col, new_al_days, wbf['content_float_border'])
            # Leave Taken
            col += 1
            worksheet.write(count, col, c_alt, wbf['content_float_border'])
            # Encash
            col += 1
            worksheet.write(count, col, encashed_days, wbf['content_float_border'])
            # Balance Days
            col += 1
            worksheet.write(count, col, annualleave_days, wbf['content_float_border'])
            # Balance Amount
            col += 1
            worksheet.write(count, col, annualleave_amount, wbf['content_float_border'])
            # Provision Date
            col += 1
            worksheet.write(count, col, last_leave_pb_date_str, wbf['content_float_border'])
            # Provision Amount
            col += 1
            worksheet.write(count, col, net_leave_amount, wbf['content_float_border'])

        count += 2
        # SUMMARY
        worksheet.merge_range('A%s:M%s' % (count, count), 'Total', wbf['content_border_bg_total'])
        worksheet.write_formula('N%s' % (count), '=SUM(N3:N%s)' % (count - 1), wbf['content_border_bg_total'])
        worksheet.write(count - 1, 14, "", wbf['content_border_bg'])
        worksheet.write_formula('P%s' % (count), '=SUM(P3:P%s)' % (count - 1), wbf['content_border_bg_total'])

        workbook.close()
        out = base64.encodebytes(fp.getvalue())
        self.write({'datas': out, 'datas_fname': filename})
        fp.close()
        filename += '%2Exlsx'
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/?model=' + self._name + '&id=' + str(
                self.id) + '&field=datas&download=true&filename=' + filename,
        }
