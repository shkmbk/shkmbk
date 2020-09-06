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

class MbkBillSummary(models.TransientModel):
    _name = 'mbk.wizard.report.billsummary'

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string="To Date", required=True)
    partner_id = fields.Many2one('res.partner',"Supplier")
    analytic_id = fields.Many2one('account.analytic.account',"Analytic Account")

    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)    


    def _get_partner(self):
        if self.partner_id:
            return ('partner_id', '=', self.partner_id.id)
        else:
            return (1, '=', 1)

    def _get_analytic(self):
        if self.analytic_id:
            return ('analytic_id', '=', self.analytic_id.id)
        else:
            return (1, '=', 1)            

    def _getdomainfilter(self):
        return [('date', '>=', self.from_date), ('date', '<=', self.to_date),self._get_partner(),
                self._get_analytic(),('company_id', '=', self.env.company.id),('state', '=', 'posted'),('type', 'in', ['in_invoice','in_refund'])
                ]

    def print_bill_summary_pdf(self):
     
        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))

        objbill = self.env['account.move'].search(self._getdomainfilter())

        if not objbill:
            raise UserError(_('There are no bills found for selected parameters'))

        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            date = pytz.utc.localize(datetime.now()).astimezone(tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            date = datetime.now()
            time = datetime.now()
        date_string =  self.to_date.strftime("%B-%y")

        report_name = 'Bill_Summary_'+ date.strftime("%y%m%d%H%M%S")
        filename = '%s %s' % (report_name, date_string)
        
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

        count = 0

        # Report Heading
        worksheet.merge_range('A%s:I%s'%(1,1), 'BILL SUMMARY REPORT', wbf['header'])
        count += 1
        col=0
        column_width=6
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Sl. No.', wbf['content_border_bg'])
        col += 1
        column_width = 20
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Bill No', wbf['content_border_bg'])
        col += 1
        column_width = 11
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Date', wbf['content_border_bg'])
        col += 1
        column_width = 40
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Supplier', wbf['content_border_bg'])
        col += 1
        column_width = 50
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Description', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Amount', wbf['content_border_bg'])
        col += 1
        column_width = 10
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'VAT', wbf['content_border_bg'])
        col += 1
        column_width = 13
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Total', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Balance', wbf['content_border_bg'])

        sum_untaxed=0.0
        sum_tax=0.0
        sum_amount=0.0
        sum_due =0.0

        for rec in objbill:
            count += 1
            col=0
            #SEQ
            worksheet.write(count, col, count-1,  wbf['content_border'])
            # Bill No
            col += 1
            worksheet.write(count, col, rec.ref, wbf['content_border'])
            
            # Date
            col += 1
            worksheet.write(count, col, rec.date.strftime("%d-%m-%Y"), wbf['content_border'])

            # Supplier
            col += 1
            worksheet.write(count, col, rec.partner_id.name, wbf['content_border'])
            # Desciption
            col += 1
            if rec.narration:
                worksheet.write(count, col, rec.narration, wbf['content_border'])
            else:
                worksheet.write(count, col, '', wbf['content_border'])
            # Amount
            col+=1
            sum_untaxed+=rec.amount_untaxed
            worksheet.write(count, col, rec.amount_untaxed,  wbf['content_border'])
            # Tax
            col+=1
            
            worksheet.write(count, col, rec.amount_total-rec.amount_untaxed,  wbf['content_float_border'])
            # Net Amount
            col+=1
            sum_amount += rec.amount_total
            worksheet.write(count, col, rec.amount_total,  wbf['content_float_border'])
            # Balance
            col+=1
            sum_due += rec.amount_residual
            worksheet.write(count, col, rec.amount_residual,  wbf['content_float_border'])

        count+=2
        # SUMMARY
        worksheet.merge_range('A%s:E%s'%(count,count), 'Total', wbf['content_border_bg_total'])
        col =5
        worksheet.write(count - 1, col,sum_untaxed, wbf['content_float_border_bg'])

        col+=1
        worksheet.write(count - 1, col, sum_amount-sum_untaxed, wbf['content_float_border_bg'])

        col += 1
        worksheet.write(count - 1, col, sum_amount, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_due, wbf['content_float_border_bg'])        

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