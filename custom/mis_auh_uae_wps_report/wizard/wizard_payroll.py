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

class WizardPayroll(models.TransientModel):
    _name = 'wps.wizard.payroll'

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))

    report_file = fields.Char()
    name = fields.Char(string="File Name")
    args = []
    date = fields.Datetime()
    time = fields.Datetime()
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    days = fields.Integer(string="Days of Payment", readonly=True, store=True)
    salary_month = fields.Selection([('01', 'January'),
                                     ('02', 'February'),
                                     ('03', 'March'),
                                     ('04', 'April'),
                                     ('05', 'May'),
                                     ('06', 'June'),
                                     ('07', 'July'),
                                     ('08', 'August'),
                                     ('09', 'September'),
                                     ('10', 'October'),
                                     ('11', 'November'),
                                     ('12', 'December')
                                     ], string="Month of Salary", readonly=True)

    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)
    hr_department_ids = fields.Many2many('hr.department', string='Department(s)')
    category_ids = fields.Many2many('hr.employee.category', string='Tags')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    payment_method = fields.Many2one('mis.hr.paymentmethod', string="Payment Method")
    employee_id = fields.Many2one('hr.employee', string='Employee', domian="[('status', '!=', 'draft')]")

    def _get_hr_tags(self):
        if self.category_ids:
            return ('employee_id.category_ids', 'in', self.category_ids.ids)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_employee(self):
        if self.employee_id:
            return ('employee_id', '=', self.employee_id.id)
        else:
            return (1, '=', 1)

    def _get_analytic_account(self):
        if self.analytic_account_id:
            return ('employee_id.contract_ids.analytic_account_id', '=', self.analytic_account_id.id)
        else:
            return ('company_id', '=', self.env.company.id)
    def _get_payment_method(self):
        if self.payment_method:
            return ('employee_id.payment_method', '=', self.payment_method.id)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_analytic_tag_ids(self):
        if self.analytic_tag_ids:
            return ('employee_id.contract_ids.x_analytic_tag_ids', 'in', self.analytic_tag_ids.ids)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_department_ids(self):
        if self.hr_department_ids:
            return ('employee_id.department_id', 'in', self.hr_department_ids.ids)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_filtered_domain(self):
        return [('date_from', '>=', self.start_date), ('date_to', '<=', self.end_date),
                self._get_hr_tags(), self._get_analytic_account(), self._get_analytic_tag_ids(),
                self._get_department_ids(), self._get_payment_method(), self._get_employee(),
                ('company_id', '=', self.env.company.id)]


    @api.onchange('start_date', 'end_date')
    def on_date_change(self):
        if self.start_date and self.end_date:
            start = str(self.start_date).split('-')
            end = str(self.end_date).split('-')
            self.days = 1 + (date(year=int(end[0]), month=int(end[1]), day=int(end[2]))
                             - date(year=int(start[0]), month=int(start[1]), day=int(start[2]))).days
            if start[1] == end[1]:
                self.salary_month = start[1]

    def print_payroll_xlsx(self):
        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))
        if self.start_date > self.end_date:
            raise UserError(_('End date should be greater than or equal to start Date'))

        slips = self.env['hr.payslip'].search(self._get_filtered_domain(), order="employee_id, number")

        if not slips:
            raise UserError(_(self._get_filtered_domain()))

        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            date = pytz.utc.localize(datetime.now()).astimezone(tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            date = datetime.now()
            time = datetime.now()

        start = str(self.start_date).split('-')
        end = str(self.end_date).split('-')
        if start[1] == end[1]:
            report_head = 'THE MONTH '+self.end_date.strftime("%B %Y").upper()
            report_footer = 'PVT OFF SALARY - '+self.end_date.strftime("%b %Y").upper()
        else:
            report_head = self.start_date.strftime("%d/%m/%Y").upper()+' - ' + self.end_date.strftime("%d/%m/%Y").upper()
            report_footer = self.start_date.strftime("%m %y").upper()+' - ' + self.end_date.strftime("%m %y").upper()
        date_string = self.end_date.strftime("%B-%y")

        report_name = 'PayrollReport_'+ date.strftime("%y%m%d%H%M%S")
        filename = '%s %s' % (report_name, date_string)


        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf = {}

        wbf['content'] = workbook.add_format()
        wbf['header'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'valign': 'center'})
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

        wbf['content_border_bg_total'] = workbook.add_format({'align': 'right', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_border_bg_total'].set_top()
        wbf['content_border_bg_total'].set_bottom()
        wbf['content_border_bg_total'].set_left()
        wbf['content_border_bg_total'].set_right()
        
        wbf['content_signature'] = workbook.add_format({'align': 'center', 'bold': 1})
        wbf['content_signature'].set_top(6)

        wbf['content_border_bg'] = workbook.add_format({'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_border_bg'].set_top()
        wbf['content_border_bg'].set_bottom()
        wbf['content_border_bg'].set_left()
        wbf['content_border_bg'].set_right()
        wbf['content_float_border_bg'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_float_border_bg'].set_top()
        wbf['content_float_border_bg'].set_bottom()
        wbf['content_float_border_bg'].set_left()
        wbf['content_float_border_bg'].set_right()

        worksheet = workbook.add_worksheet(report_footer)
        worksheet.center_horizontally()
        worksheet.set_landscape()
        worksheet.set_margins(left=.2, right=.2, top=.60, bottom=.50)
        worksheet.fit_to_pages(1, 0)
        worksheet.set_footer('&L&A'+'&RPage &P of &N', {'margin': .15})
        worksheet.set_row(0, 20)
        worksheet.merge_range('A%s:R%s' % (1, 1), 'PVT.OFFICE OF H.H.SHK.MOHAMMED BIN KHALIFA BIN ZAYED AL NAHYAN', wbf['header'])
        worksheet.set_row(1, 20)
        worksheet.merge_range('A%s:R%s' % (2, 2), 'SALARY SHEET FOR '+report_head, wbf['header'])

        col = 0
        column_width=6
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Sl. No.', wbf['content_border_bg'])
        col = 1
        column_width = 40
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Employee Name', wbf['content_border_bg'])
        col = 2
        column_width = 21
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Designation', wbf['content_border_bg'])
        col = 3
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Division', wbf['content_border_bg'])
        col = 4
        column_width = 25
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Department', wbf['content_border_bg'])
        col = 5
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Payment Mode', wbf['content_border_bg'])
        col = 6
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Contract Salary', wbf['content_border_bg'])
        col = 7
        column_width = 5
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Days', wbf['content_border_bg'])
        col = 8
        column_width = 10
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Basic Salary', wbf['content_border_bg'])
        col = 9
        column_width = 10
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Allowance', wbf['content_border_bg'])
        col = 10
        column_width = 8
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Fixed OT', wbf['content_border_bg'])
        col = 11
        column_width = 9
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'L.Salary', wbf['content_border_bg'])
        col = 12
        column_width = 8
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Air Ticket', wbf['content_border_bg'])
        col = 13
        column_width = 10
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'EOSB', wbf['content_border_bg'])
        col = 14
        column_width = 13
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Gross Amount', wbf['content_border_bg'])
        col = 15
        column_width = 13
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Fine & Penalty', wbf['content_border_bg'])
        col = 16
        column_width = 10
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'S. Advance', wbf['content_border_bg'])

        col = 17
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(2, col, 'Net Salary', wbf['content_border_bg'])

        count = 2
        sum_basic_allow = 0.0
        sum_basic = 0.0
        sum_allowance = 0.0
        sum_fixedot = 0.0
        sum_lsalary = 0.0
        sum_ticketallow = 0.0
        sum_eosb = 0.0
        sum_gross_amount = 0.0
        sum_fine_penalty = 0.0
        sum_advance = 0.0
        sum_net = 0.0
        for rec in slips:
            count += 1
            col=0
            #SEQ
            worksheet.write(count, col, count,  wbf['content_border'])
            col += 1
            # Name
            worksheet.write(count, col, rec.employee_id.name, wbf['content_border'])
            # JOB
            col += 1
            worksheet.write(count, col, rec.employee_id.job_id.name, wbf['content_border'])
            # DIVISION
            col += 1
            worksheet.write(count, col, rec.employee_id.contract_id.analytic_account_id.name, wbf['content_border'])
            # DEPARTMENT
            col += 1
            worksheet.write(count, col, rec.employee_id.department_id.name, wbf['content_border'])
            # PAYMENT METHOD
            col += 1
            worksheet.write(count, col, rec.employee_id.payment_method.name,  wbf['content_border'])
            # CONTRACT SALARY (BASIC + ALLOWANCE)
            col += 1

            basic_allow = rec.employee_id.contract_id.wage+rec.employee_id.contract_id.x_house_rent+rec.employee_id.contract_id.x_transport+rec.employee_id.contract_id.x_other_allowance+rec.employee_id.contract_id.x_fixed_ot
            worksheet.write(count, col, basic_allow,  wbf['content_float_border'])
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

            col += 1
            worksheet.write(count, col, worked_days,  wbf['content_float_border'])
            # BASIC AFTER UNPAID
            col += 1
            worksheet.write(count, col, amount_basic, wbf['content_float_border'])
            # ALLOWANCE AFTER UNPAID
            col += 1
            worksheet.write(count, col, amount_allow, wbf['content_float_border'])
            # FIX OT
            col += 1
            worksheet.write(count, col, amount_fot, wbf['content_float_border'])
            # LEAVE SALARY
            col += 1
            worksheet.write(count, col, amount_ls, wbf['content_float_border'])
            # TICKET ALLOWANCE AKA AIR TICKET
            col += 1
            worksheet.write(count, col, amount_at, wbf['content_float_border'])
            # EOSB
            col += 1
            worksheet.write(count, col, amount_esob, wbf['content_float_border'])
            # GROSS
            col += 1
            worksheet.write(count, col, amount_gross, wbf['content_float_border'])
            # FINE
            col += 1
            worksheet.write(count, col, amount_fine, wbf['content_float_border'])
            # ADVANCE
            col += 1
            worksheet.write(count, col, amount_adv, wbf['content_float_border'])
            # NET
            col += 1
            worksheet.write(count, col, amount_net, wbf['content_float_border'])
            #ADDING to sum
            sum_basic_allow += basic_allow
            sum_basic += amount_basic
            sum_allowance += amount_allow
            sum_fixedot += amount_fot
            sum_lsalary += amount_ls
            sum_ticketallow += amount_at
            sum_eosb += amount_esob
            sum_gross_amount += amount_gross
            sum_fine_penalty += amount_fine
            sum_advance += amount_adv
            sum_net += amount_net

        count += 2
        # SUMMARY
        worksheet.merge_range('A%s:F%s'%(count,count), 'Total', wbf['content_border_bg_total'])
        worksheet.write(count-1, 6, sum_basic_allow, wbf['content_float_border_bg'])
        worksheet.write(count - 1, 7, "", wbf['content_border_bg'])
        col = 7
        col += 1
        worksheet.write(count - 1, col, sum_basic, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_allowance, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_fixedot, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_lsalary, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_ticketallow, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_eosb, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_gross_amount, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_fine_penalty, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_advance, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_net, wbf['content_float_border_bg'])
        # Signtaure option
        worksheet.write(count + 4, 1, "Accounts Department", wbf['content_signature'])
        worksheet.merge_range('E%s:F%s'%(count + 5,count + 5), 'Authorized By', wbf['content_signature'])

        workbook.close()
        out=base64.encodebytes(fp.getvalue())
        self.write({'datas': out, 'datas_fname': filename})
        fp.close()
        filename += '%2Exlsx'

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/?model='+self._name+'&id='+str(self.id)+'&field=datas&download=true&filename='+filename,
        }

    def print_payroll(self):
        data = {}
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date
        data['hr_department_ids'] = self.hr_department_ids.ids
        data['category_ids'] = self.category_ids.ids
        data['analytic_account_id'] = self.analytic_account_id.id
        data['analytic_tag_ids'] = self.analytic_tag_ids.ids
        data['payment_method'] = self.payment_method.id
        data['employee_id'] = self.employee_id.id
        report = self.env.ref('mis_auh_uae_wps_report.payroll_report')
        return report.report_action(self, data=data)