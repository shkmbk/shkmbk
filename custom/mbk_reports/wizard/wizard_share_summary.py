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

class MbkStockSummary(models.TransientModel):
    _name = 'mbk.wizard.report.sharesummary'
    _description = "Inventory Summary Report Wizard"

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))

    from_date = fields.Date(default='2020-06-01', string='From Date', required=True)
    to_date = fields.Date(default=fields.Date.to_string(date.today()), string="To Date", required=True)
    product_id = fields.Many2one('product.product', "Product",  domain="[('type', '=', 'product')]")


    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)    


    def _get_product(self):
        if self.product_id:
            return ('product_id', '=', self.product_id.id)
        else:
            return ('product_id.type', '=', 'product')
          

    def _getdomainfilter(self):
        return [('create_date', '<=', self.to_date),('company_id', '=', self.env.company.id), self._get_product()]

    def print_share_summary_pdf(self):
     
        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))

        objstockval = self.env['stock.valuation.layer'].search(self._getdomainfilter())


        if not objstockval:
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
        dt_string = self.to_date.strftime("%d/%m/%Y")

        report_name = 'Stock_Summary_'+ date.strftime("%y%m%d%H%M%S")
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

        wbf['content_qty_border'] = workbook.add_format({'align': 'right', 'num_format': '#,##0'})
        wbf['content_qty_border'].set_top()
        wbf['content_qty_border'].set_bottom()
        wbf['content_qty_border'].set_left()
        wbf['content_qty_border'].set_right()

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
        
        wbf['content_border_bg_c'] = workbook.add_format({'align': 'center','bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_border_bg_c'].set_top()
        wbf['content_border_bg_c'].set_bottom()
        wbf['content_border_bg_c'].set_left()
        wbf['content_border_bg_c'].set_right()        

        wbf['content_float_border_bg'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_float_border_bg'].set_top()
        wbf['content_float_border_bg'].set_bottom()
        wbf['content_float_border_bg'].set_left()
        wbf['content_float_border_bg'].set_right()

        wbf['content_qty_border_bg'] = workbook.add_format({'align': 'right', 'num_format': '#,##0', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_qty_border_bg'].set_top()
        wbf['content_qty_border_bg'].set_bottom()
        wbf['content_qty_border_bg'].set_left()
        wbf['content_qty_border_bg'].set_right()


        

        worksheet = workbook.add_worksheet(report_name)

        count = 0

        # Report Heading
        worksheet.merge_range('A%s:K%s'%(1,1), 'STOCK SUMMARY REPORT AS ON '+dt_string, wbf['header'])
        
        count += 2
        col=0
        column_width=6
        worksheet.set_column(col, col, column_width)
        worksheet.merge_range('A2:A3', 'Sl. No.', wbf['content_border_bg_c'])
     
        col += 1
        column_width = 30
        worksheet.set_column(col, col, column_width)
        worksheet.merge_range('B2:B3', 'Product', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.merge_range('C2:D2', 'Opening', wbf['content_border_bg_c'])
        worksheet.write(count, col, 'Qty', wbf['content_border_bg'])
        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Amount', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.merge_range('E2:F2', 'Purchase', wbf['content_border_bg_c'])
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Qty', wbf['content_border_bg'])
        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Amount', wbf['content_border_bg'])        
        col += 1
        column_width = 12
        worksheet.merge_range('G2:H2', 'Sales', wbf['content_border_bg_c'])
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Qty', wbf['content_border_bg'])
        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Amount', wbf['content_border_bg'])        
        col += 1
        column_width = 12
        worksheet.merge_range('I2:K2', 'Closing', wbf['content_border_bg_c'])
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Qty', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Cost', wbf['content_border_bg'])          
        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Amount', wbf['content_border_bg'])        

        sum_opening_qty=0.0
        sum_opening_amt=0.0
        sum_in_qty=0.0
        sum_in_amt=0.0
        sum_out_qty=0.0
        sum_out_amt=0.0
        sum_closing_qty =0.0
        sum_closing_amt =0.0
        unit_cost=0.00

        for prd in objstockval.product_id:
            sm= self.env['stock.valuation.layer'].search([('company_id', '=', self.env.company.id), self._get_product(),('product_id','=',prd.id)])
            opening_qty=0.0
            opening_amt=0.0
            in_qty=0.0
            in_amt=0.0
            out_qty=0.0
            out_amt=0.0
            closing_qty =0.0
            closing_amt =0.0
            for rec in sm:
                #opening Qty
                if rec.create_date.date()< self.from_date:                
                    opening_qty+=rec.quantity
                    opening_amt+=rec.value                
                #In Qty
                
                if rec.create_date.date()>=self.from_date and rec.create_date.date()<=self.to_date:
                    if rec.quantity>0:
                        in_qty+=rec.quantity
                        in_amt+=rec.value
                #Out Qty
                if rec.create_date.date()>=self.from_date and rec.create_date.date()<=self.to_date:
                    if rec.quantity<0:
                        out_qty+=rec.quantity
                        out_amt+=rec.value
                #Closing 
                if rec.create_date.date()<= self.to_date:
                    closing_qty+=rec.quantity
                    closing_amt+=rec.value
                                     
            if closing_qty==0:         
                unit_cost=0
            else:
                unit_cost=closing_amt/closing_qty
            count += 1
            col=0
            #SEQ
            worksheet.write(count, col, count-2,  wbf['content_border'])

            # Product
            col += 1
            worksheet.write(count, col, rec.product_id.name, wbf['content_border'])

            # Opening Qty
            col+=1
            worksheet.write(count, col, opening_qty,  wbf['content_qty_border'])
            col+=1
            worksheet.write(count, col, opening_amt,  wbf['content_float_border'])
            # In Qty
            col+=1           
            worksheet.write(count, col, in_qty,  wbf['content_qty_border'])
            col+=1           
            worksheet.write(count, col, in_amt,  wbf['content_float_border'])
            # Out Qty
            col+=1
            worksheet.write(count, col, -out_qty,  wbf['content_qty_border'])
            col+=1
            worksheet.write(count, col, -out_amt,  wbf['content_float_border'])            
            # Closing Qty
            col+=1
            worksheet.write(count, col, closing_qty,  wbf['content_qty_border'])
            col+=1
            worksheet.write(count, col, unit_cost,  wbf['content_float_border'])            
            col+=1
            worksheet.write(count, col, closing_amt,  wbf['content_float_border'])
            
            sum_opening_qty+=opening_qty
            sum_opening_amt+=opening_amt
            sum_in_qty+=in_qty
            sum_in_amt+=in_amt
            sum_out_qty+=out_qty
            sum_out_amt+=out_amt
            sum_closing_qty+=closing_qty
            sum_closing_amt+=closing_amt  
            

        count+=2
        # SUMMARY
        worksheet.merge_range('A%s:B%s'%(count,count), 'Total', wbf['content_border_bg_total'])
        col =2
        worksheet.write(count - 1, col,sum_opening_qty, wbf['content_qty_border_bg'])
        col+=1
        worksheet.write(count - 1, col, sum_opening_amt, wbf['content_float_border_bg'])
        col+=1
        worksheet.write(count - 1, col, sum_in_qty, wbf['content_qty_border_bg'])
        col+=1
        worksheet.write(count - 1, col, sum_in_amt, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, -sum_out_qty, wbf['content_qty_border_bg'])
        col += 1
        worksheet.write(count - 1, col, -sum_out_amt, wbf['content_float_border_bg'])        
        col += 1
        worksheet.write(count - 1, col, sum_closing_qty, wbf['content_qty_border_bg'])
        col += 1
        worksheet.write(count - 1, col, '', wbf['content_float_border_bg'])           
        col += 1
        worksheet.write(count - 1, col, sum_closing_amt, wbf['content_float_border_bg'])        

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