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

    def _get_hr_tags(self):
        if self.category_ids:
            return ('employee_id.category_ids', 'in', self.category_ids.ids)
        else:
            return ('company_id', '=', self.env.company.id)

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
        #['&', ('date_from', '<=', self.start_date), ('date_to', '>=', self.end_date)])
        return [('date_from', '<=', self.start_date), ('date_to', '>=', self.end_date),
                self._get_hr_tags(), self._get_analytic_account(), self._get_analytic_tag_ids(),
                self._get_department_ids(), self._get_payment_method(),
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
        if self.start_date and self.end_date:
            start = str(self.start_date).split('-')
            end = str(self.end_date).split('-')
            if not start[1] == end[1]:
                raise UserError(_('The Dates Can of Same Month Only'))

        slips = self.env['hr.payslip'].search(self._get_filtered_domain())

        if not slips:
            raise UserError(_('There are no payslip Created for the selected month'))

        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            date = pytz.utc.localize(datetime.now()).astimezone(tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            date = datetime.now()
            time = datetime.now()
        date_string =  self.end_date.strftime("%B-%y")

        report_name = 'PayrollReport_'+ date.strftime("%y%m%d%H%M%S")
        filename = '%s %s' % (report_name, date_string)


        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf = {}

        wbf['content'] = workbook.add_format()
        wbf['header'] = workbook.add_format(
            {'bold': 1, 'align': 'center'})
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



        worksheet = workbook.add_worksheet(report_name)

        col=0
        column_width=6
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Sl. No.', wbf['content_border_bg'])
        col = 1
        column_width = 40
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Employee Name', wbf['content_border_bg'])
        col = 2
        column_width = 21
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Designation', wbf['content_border_bg'])
        col = 3
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Division', wbf['content_border_bg'])
        col = 4
        column_width = 25
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Department', wbf['content_border_bg'])
        col = 5
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Payment Mode', wbf['content_border_bg'])
        col = 6
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Contract Salary', wbf['content_border_bg'])
        col = 7
        column_width = 5
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Days', wbf['content_border_bg'])
        col = 8
        column_width = 10
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Basic Salary', wbf['content_border_bg'])
        col = 9
        column_width = 10
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Allowance', wbf['content_border_bg'])
        col = 10
        column_width = 8
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Fixed OT', wbf['content_border_bg'])
        col = 11
        column_width = 8
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'L.Salary', wbf['content_border_bg'])
        col = 12
        column_width = 8
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Air Ticket', wbf['content_border_bg'])
        col = 13
        column_width = 10
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'EOSB', wbf['content_border_bg'])
        col = 14
        column_width = 13
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Gross Amount', wbf['content_border_bg'])
        col = 15
        column_width = 13
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Fine & Penalty', wbf['content_border_bg'])
        col = 16
        column_width = 10
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'S. Advance', wbf['content_border_bg'])

        col = 17
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Net Salary', wbf['content_border_bg'])

        count = 0
        sum = 0
        sum_basic_allow=0.0
        sum_basic=0.0
        sum_allowance=0.0
        sum_fixedot=0.0
        sum_lsalary =0.0
        sum_ticketallow=0.0
        sum_eosb=0.0
        sum_gross_amount=0.0
        sum_fine_penalty=0.0
        sum_advance=0.0
        sum_net=0.0
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
            col+=1
            worksheet.write(count, col, rec.employee_id.payment_method.name,  wbf['content_border'])
            # CONTRACT SALARY (BASIC + ALLOWANCE)
            col+=1

            basic_allow=rec.employee_id.contract_id.wage+rec.employee_id.contract_id.x_house_rent+rec.employee_id.contract_id.x_transport+rec.employee_id.contract_id.x_other_allowance+rec.employee_id.contract_id.x_fixed_ot
            worksheet.write(count, col, basic_allow,  wbf['content_float_border'])
            # DAYS
            #worksheet.write(count, col, ((self.end_date-self.start_date).days+1),  wbf['content_border']) #For Days in Period
            worked_days=0.0
            payslip_worked_days = self.env['hr.payslip.worked_days'].search([('payslip_id', '=', rec.id), ('work_entry_type_id', '=',1)])
            if payslip_worked_days:
                worked_days=payslip_worked_days.number_of_days
            col+=1
            worksheet.write(count, col, worked_days,  wbf['content_float_border'])
            # BASIC AFTER UNPAID
            col += 1
            amountbasic = 0.0
            slipbasic = self.env['hr.payslip.line'].search([('slip_id', '=', rec.id), ('employee_id', '=', rec.employee_id.id), ('code', '=', 'BASIC')])
            if slipbasic:
                amountbasic=slipbasic.total
            worksheet.write(count, col, amountbasic, wbf['content_float_border'])
            # ALLOWANCE AFTER UNPAID
            col += 1
            amountallow = 0.0
            sliphra = self.env['hr.payslip.line'].search(
                [('slip_id', '=', rec.id), ('employee_id', '=', rec.employee_id.id), ('code', '=', 'ALW')])
            if sliphra:
                amountallow = sliphra.total
            worksheet.write(count, col, amountallow, wbf['content_float_border'])
            # FIX OT
            col += 1
            amountfixot = 0.0
            slipfixot = self.env['hr.payslip.line'].search(
                [('slip_id', '=', rec.id), ('employee_id', '=', rec.employee_id.id), ('code', '=', 'FOT')])
            if slipfixot:
                amountfixot = slipfixot.total
            worksheet.write(count, col, amountfixot, wbf['content_float_border'])
            # LEAVE SALARY
            col += 1
            amountlsal = 0.0
            sliplsal = self.env['hr.payslip.line'].search(
                [('slip_id', '=', rec.id), ('employee_id', '=', rec.employee_id.id), ('code', '=', 'LS')])
            if sliplsal:
                amountlsal = sliplsal.total
            worksheet.write(count, col, amountlsal, wbf['content_float_border'])
            # TICKET ALLOWANCE
            col += 1
            amounttall = 0.0
            sliptall = self.env['hr.payslip.line'].search(
                [('slip_id', '=', rec.id), ('employee_id', '=', rec.employee_id.id), ('code', '=', 'AT')])
            if sliptall:
                amounttall = sliptall.total
            worksheet.write(count, col, amounttall, wbf['content_float_border'])
            # EOSB
            col += 1
            amounteosb= 0.0
            slipeosb = self.env['hr.payslip.line'].search(
                [('slip_id', '=', rec.id), ('employee_id', '=', rec.employee_id.id), ('code', '=', 'EOSB')])
            if slipeosb:
                amounteosb = slipeosb.total
            worksheet.write(count, col, amounteosb, wbf['content_float_border'])
            # GROSS
            col += 1
            amountgross= 0.0
            slipgross = self.env['hr.payslip.line'].search(
                [('slip_id', '=', rec.id), ('employee_id', '=', rec.employee_id.id), ('code', '=', 'GROSS')])
            if slipgross:
                amountgross = slipgross.total
            worksheet.write(count, col, amountgross, wbf['content_float_border'])
            # FINE
            col += 1
            amountfine= 0.0
            slipfine = self.env['hr.payslip.line'].search(
                [('slip_id', '=', rec.id), ('employee_id', '=', rec.employee_id.id), ('code', '=', 'PD')])
            if slipfine:
                amountfine = slipfine.total
            worksheet.write(count, col, amountfine, wbf['content_float_border'])
            # ADVANCE
            col += 1
            amountadv= 0.0
            slipadv = self.env['hr.payslip.line'].search(
                [('slip_id', '=', rec.id), ('employee_id', '=', rec.employee_id.id), ('code', '=', 'SA')])
            if slipadv:
                amountadv = slipadv.total
            worksheet.write(count, col, amountadv, wbf['content_float_border'])
            # NET
            col += 1
            amountnet = 0.0
            slipnet = self.env['hr.payslip.line'].search([('slip_id', '=', rec.id), ('employee_id', '=', rec.employee_id.id), ('code', '=', 'NET')])
            if slipnet:
                amountnet=slipnet.total
            worksheet.write(count, col, amountnet, wbf['content_float_border'])
            #ADDING to sum
            sum_basic_allow += basic_allow
            sum_basic += amountbasic
            sum_allowance += amountallow
            sum_fixedot += amountfixot
            sum_lsalary += amountlsal
            sum_ticketallow += amounttall
            sum_eosb += amounteosb
            sum_gross_amount += amountgross
            sum_fine_penalty += amountfine
            sum_advance += amountadv
            sum_net += amountnet

        count+=2
        # SUMMARY
        worksheet.merge_range('A%s:F%s'%(count,count), 'Total', wbf['content_border_bg_total'])
        worksheet.write(count-1, 6, sum_basic_allow, wbf['content_float_border_bg'])
        worksheet.write(count - 1, 7, "", wbf['content_border_bg'])
        col=7
        col+=1
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

        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write({'datas':out, 'datas_fname':filename})
        fp.close()
        filename += '%2Exlsx'

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/?model='+self._name+'&id='+str(self.id)+'&field=datas&download=true&filename='+filename,
        }
