# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import date_utils
import xlsxwriter
import base64
from odoo import fields, models, api, _
from io import BytesIO
from pytz import timezone
import pytz

class MbkStockSummary(models.TransientModel):
    _name = 'mbk.wizard.report.farmstocksummary'
    _description = "Famr Stock Summary Report Wizard"

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))

    from_date = fields.Date(default='2020-06-01', string='From Date', required=True)
    to_date = fields.Date(default=fields.Date.to_string(date.today()), string="To Date", required=True)
    product_id = fields.Many2one('product.product',"Product", domain="[('type', 'in', ['consu','product'])]")
    partner_id = fields.Many2one('res.partner',"Partner")
    analytic_id = fields.Many2one('account.analytic.account',"Analytic Account")

    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)    


    def _get_product(self):
        if self.product_id:
            return ('product_id', '=', self.product_id.id)
        else:
            return ('product_id.type', 'in', ['consu','product'])

    def _get_analytic(self):
        if self.analytic_id:
            return ('stock_move_id.analytic_account_id', '=', self.analytic_id.id)
        else:
            return (1, '=', 1)            

    def _getdomainfilter(self):
        return [('create_date', '<=', self.to_date),('company_id', '=', self.env.company.id), self._get_product(), self._get_analytic()]

    def print_farm_stock_summary_xls(self):
     
        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))

        objstockmove = self.env['stock.valuation.layer'].search(self._getdomainfilter())


        if not objstockmove:
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
        report_name = 'Farm_Summary_'+ date.strftime("%y%m%d%H%M%S")
        filename = '%s %s' % (report_name, date_string)
        
        op_fy_date = datetime(2020, 6, 1)

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf = {}

        wbf['content'] = workbook.add_format()
        wbf['header'] = workbook.add_format({'bold': 1, 'align': 'center'})
        wbf['content_float'] = workbook.add_format({'align': 'right', 'num_format': '#,##0'})
        wbf['content_border'] = workbook.add_format()
        wbf['content_border'].set_top()
        wbf['content_border'].set_bottom()
        wbf['content_border'].set_left()
        wbf['content_border'].set_right()

        wbf['content_float_border'] = workbook.add_format({'align': 'right', 'num_format': '#,##0'})
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

        wbf['content_float_border_bg'] = workbook.add_format({'align': 'right', 'num_format': '#,##0', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_float_border_bg'].set_top()
        wbf['content_float_border_bg'].set_bottom()
        wbf['content_float_border_bg'].set_left()
        wbf['content_float_border_bg'].set_right()

        wbf['content_border_bg_c'] = workbook.add_format({'align': 'center','bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_border_bg_c'].set_top()
        wbf['content_border_bg_c'].set_bottom()
        wbf['content_border_bg_c'].set_left()
        wbf['content_border_bg_c'].set_right()  

        

        worksheet = workbook.add_worksheet(report_name)

        count = 0

        # Report Heading
        worksheet.merge_range('A%s:K%s'%(1,1), 'FARM STOCK SUMMARY REPORT AS ON '+ dt_string, wbf['header'])
        count += 2
        col=0
        column_width=6
        worksheet.set_column(col, col, column_width)
        worksheet.merge_range('A2:A3', 'Sl. No.', wbf['content_border_bg_c'])     
        col += 1
        column_width = 40
        worksheet.set_column(col, col, column_width)
        worksheet.merge_range('B2:B3', 'Product', wbf['content_border_bg_c'])    
        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.merge_range('C2:C3', 'Opening Qty', wbf['content_border_bg_c'])
        col += 1
        worksheet.merge_range('D2:E2', 'Inward Qty', wbf['content_border_bg_c'])
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Birth', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Purchase', wbf['content_border_bg'])        
        col += 1
        worksheet.merge_range('F2:H2', 'Outward Qty', wbf['content_border_bg_c'])
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Consumption', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Sale', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Death', wbf['content_border_bg'])
        col += 1
        worksheet.merge_range('I2:K2', 'Closing Qty', wbf['content_border_bg_c'])
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Immature', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Mature', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Net', wbf['content_border_bg'])

        sum_opening_qty =0.0
        sum_closing_qty =0.0
        sum_birth_qty =0.00
        sum_purchase_qty =0.00
        sum_consumption_qty =0.00
        sum_sale_qty =0.00
        sum_death_qty =0.00
        sum_immature_qty =0.00
        sum_mature_qty =0.00

        for prd in objstockmove.product_id:
            sm= self.env['stock.valuation.layer'].search([('create_date', '<=', self.to_date),('company_id', '=', self.env.company.id), self._get_product(), self._get_analytic(),('product_id','=',prd.id)])
            opening_qty=0.0
            in_qty=0.0
            out_qty=0.0
            closing_qty =0.0
            birth_qty=0.00
            purchase_qty=0.00
            consumption_qty=0.00
            sale_qty=0.00
            death_qty=0.00
            immature_qty=0.00
            mature_qty=0.00

            for rec in sm:
                
                #opening Qty
                if rec.create_date.date()< self.from_date:                
                    opening_qty+=rec.quantity 
                #In Qty
                
                if rec.create_date.date()>=self.from_date and rec.create_date.date()<=self.to_date:
                    if rec.quantity>0:
                        in_qty+=rec.quantity
                #Out Qty
                if rec.create_date.date()>=self.from_date and rec.create_date.date()<=self.to_date:
                    if rec.quantity<0:
                        out_qty+=rec.quantity
                #Balance Qty
                if rec.create_date.date()<= self.to_date:
                    closing_qty+=rec.quantity

                for wip in rec.stock_move_id.custom_analytic_tag_ids:
                    if rec.create_date.date()>=self.from_date and rec.create_date.date()<=self.to_date:
                        if rec.quantity>0:
                            if wip.name == 'Birth':
                                birth_qty+=rec.quantity
                            if wip.name == 'Purchase':
                                purchase_qty+=rec.quantity
                            if wip.name == 'Opening':
                                opening_qty+=rec.quantity
                        if rec.quantity<0:
                            if wip.name == 'Death':
                                death_qty+=rec.quantity
                            if wip.name == 'Sale':
                                sale_qty+=rec.quantity
                            if wip.name == 'Consumption':
                                consumption_qty+=rec.quantity

                    if rec.create_date.date()+ timedelta(days=rec.product_id.sale_delay)>(self.to_date) and rec.quantity>0:
                        if wip.name in ['Birth','Purchase']:
                            immature_qty+=rec.quantity
            if immature_qty>closing_qty:
                immature_qty=closing_qty
            else:
                mature_qty=closing_qty-immature_qty                         
 
            count += 1
            col=0
            #SEQ
            worksheet.write(count, col, count-2,  wbf['content_border'])

            # Product
            col += 1
            worksheet.write(count, col, rec.product_id.name, wbf['content_border'])

            # Opening Qty
            col+=1
            worksheet.write(count, col, opening_qty,  wbf['content_border'])
            # In Qty - Birth
            col+=1           
            worksheet.write(count, col, birth_qty,  wbf['content_float_border'])
            # In Qty - Purchase
            col+=1           
            worksheet.write(count, col, purchase_qty,  wbf['content_float_border'])            
            # Out Qty-Consumption
            col+=1
            worksheet.write(count, col, abs(consumption_qty),  wbf['content_float_border'])
            # Out Qty-Sales
            col+=1
            worksheet.write(count, col, abs(sale_qty),  wbf['content_float_border'])
            # Out Qty-Death
            col+=1
            worksheet.write(count, col, abs(death_qty),  wbf['content_float_border'])                          
            # Balance Qty- Inmature
            col+=1
            worksheet.write(count, col, immature_qty,  wbf['content_float_border'])
            # Balance Qty- Mature
            col+=1
            worksheet.write(count, col, mature_qty,  wbf['content_float_border'])
            # Balance Qty
            col+=1
            worksheet.write(count, col, closing_qty,  wbf['content_float_border'])       
            
            sum_opening_qty +=opening_qty
            sum_closing_qty +=closing_qty
            sum_birth_qty+=birth_qty
            sum_purchase_qty+=purchase_qty
            sum_consumption_qty +=consumption_qty
            sum_sale_qty+=sale_qty
            sum_death_qty+=death_qty
            sum_immature_qty+=immature_qty
            sum_mature_qty+=mature_qty
            

        count+=2
        # SUMMARY
        worksheet.merge_range('A%s:B%s'%(count,count), 'Total', wbf['content_border_bg_total'])
        col =2
        worksheet.write(count - 1, col,sum_opening_qty, wbf['content_float_border_bg'])
        col+=1
        worksheet.write(count - 1, col, sum_birth_qty, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_purchase_qty, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, abs(sum_consumption_qty), wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, abs(sum_sale_qty), wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, abs(sum_death_qty), wbf['content_float_border_bg'])               
        col += 1
        worksheet.write(count - 1, col, sum_immature_qty, wbf['content_float_border_bg'])          
        col += 1
        worksheet.write(count - 1, col, sum_mature_qty, wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, sum_closing_qty, wbf['content_float_border_bg'])        

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
    def print_stock_details_pdf(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        tmpdate = self.to_date
        data['product_id'] = self.product_id.id
        data['analytic_id'] = self.analytic_id.id
        data['header_date'] = tmpdate.strftime("%d-%m-%Y")
        report = self.env.ref('mbk_reports.farmstock_details_pdf')        
        return report.report_action(self, data=data)