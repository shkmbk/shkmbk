from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError

class StockDetailsReport(models.AbstractModel):
    _name = 'report.mbk_reports.report_stock_details_document'
    _description = "Stock Details Report"

    
    @api.model
    def _get_product(self,product_id):
        if product_id:
            return ('product_id', '=', product_id)
        else:
            return (1, '=', 1)

    def _get_analytic(self,analytic_id):
        if analytic_id:
            return ('picking_id.analytic_id', '=', analytic_id)
        else:
            return (1, '=', 1)            

    def _getdomainfilter(self,from_date,to_date,product_id,analytic_id):
        return [('picking_id.date_done', '<=', to_date),('company_id', '=', self.env.company.id),('state', '=', 'done'),
                self._get_product(product_id), self._get_analytic(analytic_id),('picking_id.picking_type_id.code','in',['incoming','outgoing'])]

    
    def _get_report_values(self, docids, data=None):
        from_date = data['from_date']
        to_date = data['to_date']
        product_id =data['product_id']
        analytic_id=data['analytic_id']
        header_date = data['header_date']
        
        raise UserError('Is working')
        
        
        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))
            
        objbill = self.env['stock.move'].search(self._getdomainfilter(from_date,to_date,product_id,analytic_id))

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

        report_name = 'Stock_Summary_'+ date.strftime("%y%m%d%H%M%S")
        filename = '%s %s' % (report_name, date_string)
        
        op_fy_date = datetime(2020, 6, 1)

        
        count = 0
        master_table =[]
        sum_opening=0.0
        sum_in_qty=0.0
        sum_out_qty=0.0
        sum_balance =0.0

        for rec in objbill:
            count += 1
            transaction_no=rec.picking_id.name
            date_done=rec.picking_id.date_done.strftime("%d-%m-%Y")            
            # Partner
            if rec.picking_id.partner_id:
                partner_name=rec.picking_id.partner_id.name           
            else:
                partner_name=''
            # Product
            product_name=rec.product_id.name
            # Opening Qty
            opening_qty=0.00
            if rec.picking_id.date_done.date()< self.from_date:
            
                if rec.picking_id.picking_type_id.code=='incoming':
                    sum_opening+=rec.product_qty
                    opening_qty+=rec.product_qty
                elif rec.picking_id.picking_type_id.code=='outgoing':
                    sum_opening-=rec.product_qty
                    opening_qty-=rec.product_qty             
            # In Qty
            in_qty=0.00
            
            if rec.picking_id.date_done.date()>=self.from_date and rec.picking_id.date_done.date()<=self.to_date:
                if rec.picking_id.picking_type_id.code=='incoming':
                    in_qty=rec.product_qty
                    sum_in_qty+=rec.product_qty                  
            
            # Out Qty
            out_qty=0.00
            if rec.picking_id.date_done.date()>=self.from_date and rec.picking_id.date_done.date()<=self.to_date:
                if rec.picking_id.picking_type_id.code=='outgoing':
                    sum_out_qty+=rec.product_qty
                    out_qty=rec.product_qty
            
            # Balance Qty
            if rec.picking_id.date_done.date()<= self.to_date:
                if rec.picking_id.picking_type_id.code=='incoming':
                    sum_balance+=rec.product_qty
                elif rec.picking_id.picking_type_id.code=='outgoing':
                    sum_balance-=rec.product_qty               
                        
            master_table.append({
                            'transaction_no': transaction_no,
                            'date_done': date_done,
                            'partner_name':partner_name,
                            'product_name': product_name,
                            'opening_qty': opening_qty,
                            'in_qty': in_qty,
                            'out_qty': out_qty,
                            'balance' : sum_balance,
                        })

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'report.stock.move',
            'docs': master_table,
            'to_date': to_date,
        }
        return docargs