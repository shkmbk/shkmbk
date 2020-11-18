from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from pytz import timezone
import pytz

class StockDetailsReport(models.AbstractModel):
    _name = 'report.mbk_reports.report_stock_details'
    _description = "Stock Details Report"

    
    @api.model
    def _get_product(self, product_id):
        if product_id:
            return ('product_id', '=', product_id)
        else:
            return ('product_id.type', '=', 'product')

    def _get_analytic(self, analytic_id):
        if analytic_id:
            return ('stock_move_id.analytic_account_id', '=', analytic_id)
        else:
            return (1, '=', 1)            

    def _getdomainfilter(self, from_date, to_date, product_id,analytic_id):
        return [('create_date', '<=', to_date), ('company_id', '=', self.env.company.id),
                self._get_product(product_id), self._get_analytic(analytic_id)]

    
    def _get_report_values(self, docids, data=None):
        s_from_date = data['from_date']
        s_to_date = data['to_date']
        product_id = data['product_id']
        analytic_id = data['analytic_id']
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
        #date_string =  to_date.strftime("%B-%y")

        #report_name = 'Stock_Summary_'+ date.strftime("%y%m%d%H%M%S")
        #filename = '%s %s' % (report_name, date_string)
        
        op_fy_date = datetime(2020, 6, 1)

        
        count = 0
        master_table = []
        sum_opening = 0.0
        sum_in_qty = 0.0
        sum_out_qty = 0.0
        sum_balance_qty = 0.0

        for rec in objinv:
            if rec.create_date.date() < from_date:
                sum_opening +=rec.quantity
                sum_balance_qty +=rec.quantity
            else:
                count += 1
                transaction_no = rec.description
                # Date
                trn_date=rec.create_date.strftime("%d-%m-%Y")
                # Partner
                if rec.stock_move_id.picking_id.partner_id:
                    partner_name = rec.stock_move_id.picking_id.partner_id.name
                else:
                    partner_name=''

                # Product
                product_name = rec.product_id.name
                # Opening Qty                                
                opening_qty = sum_balance_qty
                # In Qty
                in_qty=0.00
                out_qty=0.00
                
                if rec.create_date.date()>=from_date and rec.create_date.date()<=to_date:
                    if rec.quantity>0:
                        in_qty = rec.quantity
                        sum_in_qty += rec.quantity
                    if rec.quantity < 0:
                        sum_out_qty += rec.quantity
                        out_qty = rec.quantity

                # Balance Qty
                if rec.create_date.date() <= to_date:
                    sum_balance_qty += rec.quantity
                        
                master_table.append({
                                'transaction_no': transaction_no,
                                'trn_date': trn_date,
                                'partner_name':partner_name,
                                'product_name': product_name,
                                'opening_qty': opening_qty,
                                'in_qty': in_qty,
                                'out_qty': -out_qty,
                                'balance' : sum_balance_qty,
                            })

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'stock.valuation.layer',
            'docs': master_table,
            'to_date': to_date,
        }
        return docargs