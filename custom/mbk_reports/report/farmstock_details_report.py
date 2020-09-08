from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from pytz import timezone
import pytz

class FarmStockDetailsReport(models.AbstractModel):
    _name = 'report.mbk_reports.report_farmstock_details'
    _description = "Farm Stock Details Report"

    
    @api.model
    def _get_product(self,product_id):
        if product_id:
            return ('product_id', '=', product_id)
        else:
            return ('product_id.type', '=', 'consu')

    def _get_analytic(self,analytic_id):
        if analytic_id:
            return ('stock_move_id.analytic_account_id', '=', analytic_id)
        else:
            return (1, '=', 1)            

    def _getdomainfilter(self,from_date,to_date,product_id,analytic_id):
        return [('create_date', '<=', to_date),('company_id', '=', self.env.company.id),
                self._get_product(product_id), self._get_analytic(analytic_id)]

    
    def _get_report_values(self, docids, data=None):
        s_from_date = data['from_date']
        s_to_date = data['to_date']
        product_id =data['product_id']
        analytic_id=data['analytic_id']
        header_date = data['header_date']

        from_date= datetime.strptime(s_from_date, '%Y-%m-%d').date()
        to_date= datetime.strptime(s_to_date , '%Y-%m-%d').date()

         
        
        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))
            
        objinv = self.env['stock.valuation.layer'].search(self._getdomainfilter(from_date,to_date,product_id,analytic_id))

        if not objinv:
            #raise UserError('There are no stock found for selected parameters')
            raise UserError(self._getdomainfilter(from_date,to_date,product_id,analytic_id))

        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            date = pytz.utc.localize(datetime.now()).astimezone(tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            date = datetime.now()
            time = datetime.now()
        dt_string = to_date.strftime("%d/%m/%Y")
        
        op_fy_date = datetime(2020, 6, 1)

        
        count = 0
        master_table =[]
        sum_opening_qty =0.0
        sum_closing_qty =0.0
        sum_birth_qty =0.00
        sum_purchase_qty =0.00
        sum_consumption_qty =0.00
        sum_sale_qty =0.00
        sum_death_qty =0.00
        sum_immature_qty =0.00
        sum_mature_qty =0.00

        for prd in objinv.product_id:
            sv= self.env['stock.valuation.layer'].search([('create_date', '<=', to_date),('company_id', '=', self.env.company.id), self._get_analytic(analytic_id),('product_id','=',prd.id)])
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
            product_name=''

            for rec in sv:
                
                product_name=rec.product_id.name
                #opening Qty
                if rec.create_date.date()< from_date:                
                    opening_qty+=rec.quantity                  
                #In Qty
                
                if rec.create_date.date()>=from_date and rec.create_date.date()<=to_date:
                    if rec.quantity>0:
                        in_qty+=rec.quantity
                #Out Qty
                if rec.create_date.date()>=from_date and rec.create_date.date()<=to_date:
                    if rec.quantity<0:
                        out_qty+=rec.quantity
                #Balance Qty
                if rec.create_date.date()<= to_date:
                    closing_qty+=rec.quantity

                for wip in rec.stock_move_id.custom_analytic_tag_ids:
                    if rec.create_date.date()>=from_date and rec.create_date.date()<=to_date:
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

                    if rec.create_date.date()+ timedelta(days=rec.product_id.sale_delay)>(to_date) and rec.quantity>0:
                        if wip.name in ['Birth','Purchase']:
                            immature_qty+=rec.quantity
            if immature_qty>closing_qty:
                immature_qty=closing_qty
            else:
                mature_qty=closing_qty-immature_qty

            master_table.append({
                            'product_name': product_name,
                            'opening_qty': opening_qty,
                            'birth_qty': birth_qty,
                            'purchase_qty':purchase_qty,
                            'consumption_qty': abs(consumption_qty),
                            'sale_qty': abs(sale_qty),
                            'death_qty': abs(death_qty),
                            'immature_qty': immature_qty,
                            'mature_qty' : mature_qty,
                            'net_qty' : closing_qty,
                        })            

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'stock.valuation.layer',
            'docs': master_table,
            'to_date': to_date,
        }
        return docargs