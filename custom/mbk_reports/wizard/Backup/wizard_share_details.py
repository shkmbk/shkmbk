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

class MbkShareDetailsW(models.TransientModel):
    _name = 'mbk.wizard.report.sharedetails'

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string="To Date", required=True)
    product_id = fields.Many2one('product.product',"Product",required=True)


    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)    


    def _get_product(self):
        if self.product_id:
            return ('product_id', '=', self.product_id.id)
        else:
            return (1, '=', 1)
          

    def _getdomainfilter(self):
        return [('create_date', '<=', self.to_date),('company_id', '=', self.env.company.id), self._get_product()]

    def print_share_details_pdf(self):
     
        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))

        objbill = self.env['stock.valuation.layer'].search(self._getdomainfilter())

        if not objbill:
            raise UserError('There are no stock found for selected parameters')

        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            date = pytz.utc.localize(datetime.now()).astimezone(tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            date = datetime.now()
            time = datetime.now()
        date_string =  self.to_date.strftime("%B-%y")
        product_name= objbill.product_id.name[0] 

        report_name = 'Stock_Details_'+ date.strftime("%y%m%d%H%M%S")
        filename = '%s %s' % (report_name, date_string)
        dt_string = self.to_date.strftime("%d/%m/%Y")
        
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
        worksheet.merge_range('A%s:K%s'%(1,1), 'STOCK DETAILS OF '+product_name+' AS ON '+ dt_string, wbf['header'])
        count += 1
        col=0
        column_width=6
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Sl. No.', wbf['content_border_bg'])
        col += 1
        column_width = 18
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Transaction Details', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Date', wbf['content_border_bg'])
        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Partner', wbf['content_border_bg'])        
        col += 1
        column_width = 20
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Product', wbf['content_border_bg'])
        col += 1
        column_width = 10
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Opening Qty', wbf['content_border_bg'])
        col += 1
        column_width = 9
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'In Qty', wbf['content_border_bg'])
        col += 1
        column_width = 9
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Out Qty', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Closing Qty', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Cost', wbf['content_border_bg'])        
        col += 1        
        column_width = 15
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Closing Amount', wbf['content_border_bg'])

        sum_opening=0.0
        sum_in_qty=0.0
        sum_out_qty=0.0
        sum_balance_qty =0.0
        sum_balance_amt=0.00
        unit_cost=0.00
        unit_rate=0.00

        for rec in objbill:
            count += 1
            col=0
            #SEQ
            worksheet.write(count, col, count-1,  wbf['content_border'])
            # Transaction Numeber
            col += 1
            worksheet.write(count, col, rec.description, wbf['content_border'])
            
            # Date
            col += 1
            worksheet.write(count, col, rec.create_date.strftime("%d-%m-%Y"), wbf['content_border'])
            
            # Partner
            col += 1
            if rec.stock_move_id.partner_id:
                worksheet.write(count, col, rec.stock_move_id.partner_id.name, wbf['content_border'])            
            else:
                worksheet.write(count, col,'', wbf['content_border'])  

            # Product
            col += 1
            worksheet.write(count, col, rec.product_id.name, wbf['content_border'])

            # Opening Qty
            col+=1
            opening_qty=0.00
            if rec.create_date.date()< self.from_date:
                sum_opening+=rec.quantity
                opening_qty+=rec.quantity

                    
            
            worksheet.write(count, col, opening_qty,  wbf['content_border'])
            # In Qty
            col+=1
            in_qty=0.00
            
            if rec.create_date.date()>=self.from_date and rec.create_date.date()<=self.to_date:
                if rec.quantity>0:
                    in_qty=rec.quantity
                    sum_in_qty+=rec.quantity
                    
            
            worksheet.write(count, col, in_qty,  wbf['content_float_border'])
            # Out Qty
            col+=1
            out_qty=0.00
            if rec.create_date.date()>=self.from_date and rec.create_date.date()<=self.to_date:
                if rec.quantity<0:
                    sum_out_qty+=rec.quantity
                    out_qty=rec.quantity

            worksheet.write(count, col, -out_qty,  wbf['content_float_border'])
            # Balance Qty
            col+=1
            if rec.create_date.date()<= self.to_date:
                sum_balance_qty+=rec.quantity
                sum_balance_amt+=rec.value              
                          
            worksheet.write(count, col, sum_balance_qty,  wbf['content_float_border'])
            # cost
            col+=1
            if sum_balance_qty==0:         
                unit_cost=0
            else:
                unit_cost=sum_balance_amt/sum_balance_qty
            unit_rate= rec.unit_cost
            worksheet.write(count, col, unit_cost,  wbf['content_float_border'])
            
            col += 1
            worksheet.write(count, col, sum_balance_amt,  wbf['content_float_border'])

        count+=2
        # SUMMARY
        worksheet.merge_range('A%s:E%s'%(count,count), 'Total', wbf['content_border_bg_total'])
        col =5
        worksheet.write(count - 1, col,sum_opening, wbf['content_float_border_bg'])

        col+=1
        worksheet.write(count - 1, col, sum_in_qty, wbf['content_float_border_bg'])

        col += 1
        worksheet.write(count - 1, col, -sum_out_qty, wbf['content_float_border_bg'])
        
        col += 1        
        worksheet.write(count - 1, col, sum_balance_qty, wbf['content_float_border_bg'])
        col += 1        
        worksheet.write(count - 1, col, unit_cost, wbf['content_float_border_bg'])        
        col += 1        
        worksheet.write(count - 1, col, sum_balance_amt, wbf['content_float_border_bg'])        

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
        