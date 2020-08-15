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

class Wizard(models.TransientModel):
    _name = 'wps.wizard'

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

    def print_xlsx(self):
        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))
        if self.start_date and self.end_date:
            start = str(self.start_date).split('-')
            end = str(self.end_date).split('-')
            if not start[1] == end[1]:
                raise UserError(_('The Dates Can of Same Month Only'))
        #return self.env['hr.employee'].search(self._get_available_contracts_domain())
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

        datetime_string = self.get_default_date_model().strftime("%Y-%m-%d %H:%M:%S")
        date_string = self.get_default_date_model().strftime("%Y-%m-%d")
        date_string =  self.end_date.strftime("%B-%y")

        report_name = 'WPS_'+ date.strftime("%y%m%d%H%M%S")
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


        worksheet = workbook.add_worksheet(report_name)
        worksheet2 = workbook.add_worksheet("Summary")
        worksheet2.merge_range('A1:E1', 'EMPLOYEES SALARY', wbf['header'])

        col=0
        column_width=30
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Beneficiary Bank Name', wbf['content'])
        worksheet2.set_column(col, col, 10)
        worksheet2.write(1, col, 'SL No', wbf['content_border'])
        col = 1
        column_width = 15
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Bank Routing Code', wbf['content'])
        worksheet2.set_column(col, col, 25)
        worksheet2.write(1, col, 'EMPLOYEES NAME', wbf['content_border'])
        col = 2
        column_width = 15
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Transaction Type', wbf['content'])
        worksheet2.set_column(col, col, 25)
        worksheet2.write(1, col, 'NAME OF BANK', wbf['content_border'])
        col = 3
        column_width = 15
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Transaction Code', wbf['content'])
        worksheet2.set_column(col, col, 25)
        worksheet2.write(1, col, 'IBAN NUMBER', wbf['content_border'])
        col = 4
        column_width = 30
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Beneficiary Name (Max.140 characters)', wbf['content'])        
        worksheet2.set_column(col, col, 15)
        worksheet2.write(1, col, 'SALARY AED', wbf['content_border'])
        col = 5
        column_width = 30
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Beneficiary IBAN No. (Max. 23 charcters)', wbf['content'])        
        col = 6
        column_width = 20
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Amount (Only 2 decimals)', wbf['content'])        
        col = 7
        column_width = 30
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Remittance Information (Max. 135 characters)', wbf['content'])
        worksheet.write(0, col, 'Transfer Month(MMM-YY)', wbf['content'])
        col = 8
        column_width = 15
        worksheet.set_column(col, col, column_width)
        worksheet.write(0, col, 'Transfer Month(MMM-YY)', wbf['content'])        


        count = 0
        sum = 0
        monthyear = self.end_date
        monthyear = str(monthyear).split('-')
        monthyear = str(monthyear[1]) + str(monthyear[0])

        for rec in slips:
            count += 1
            col=0
            worksheet.write(count, col, rec.employee_id.agent_id.name, wbf['content_border'])
            worksheet2.write(count+1, col, count, wbf['content_border'])
            col += 1
            worksheet.write(count, col,rec.employee_id.agent_id.routing_code,  wbf['content'])
            col += 1
            worksheet.write(count, col, "Salary", wbf['content'])
            col += 1
            worksheet.write(count, col, "SAL", wbf['content'])
            col += 1
            worksheet.write(count, col, rec.employee_id.full_name, wbf['content'])
            worksheet2.write(count + 1, 1, rec.employee_id.full_name, wbf['content_border'])
            col+=1
            worksheet.write(count, col, rec.employee_id.iban_number,  wbf['content'])
            worksheet2.write(count + 1, 2, rec.employee_id.agent_id.name, wbf['content_border'])
            worksheet2.write(count+1, 3, rec.employee_id.iban_number, wbf['content_border'])            
            col += 1
            slipline = self.env['hr.payslip.line'].search([('slip_id', '=', rec.id), ('employee_id', '=', rec.employee_id.id), ('code', '=', 'NET')])
            amount=0.0
            if slipline:
                amount=slipline.total

            worksheet.write(count, col, amount, wbf['content_float'])
            worksheet2.write(count + 1, 4, amount,  wbf['content_float_border'])
            sum+=amount
            col += 1
            worksheet.write(count, col, "Salary Transfer", wbf['content'])
            col += 1
            worksheet.write(count, col, date_string, wbf['content'])
        count+=2
        worksheet2.merge_range('A%s:D%s'%(count,count), 'Total', wbf['content_border'])
        worksheet2.write(count-1, 4, sum, wbf['content_float_border'])

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




