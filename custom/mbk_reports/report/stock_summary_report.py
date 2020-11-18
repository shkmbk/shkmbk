from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from pytz import timezone
import pytz

class StockSummaryReport(models.AbstractModel):
    _name = 'report.mbk_reports.report_stock_summary'
    _description = "Stock Summary Report"

    
    @api.model
    def _get_product(self, product_id):
        if product_id:
            return ('product_id', '=', product_id)
        else:
            return ('product_id.type', '=', 'product')

    def _getdomainfilter(self, product_id, to_date):
        return [('create_date', '<=', to_date), ('company_id', '=', self.env.company.id), self._get_product(product_id)]

    
    def _get_report_values(self, docids, data=None):
        s_from_date = data['from_date']
        s_to_date = data['to_date']
        product_id = data['product_id']
        header_date = data['header_date']

        from_date = datetime.strptime(s_from_date, '%Y-%m-%d').date()
        to_date = datetime.strptime(s_to_date, '%Y-%m-%d').date()

        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))

        objstockval = self.env['stock.valuation.layer'].search(self._getdomainfilter(product_id, to_date))

        if not objstockval:
            raise UserError('There are no transaction found for selected parameters')

        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            date = pytz.utc.localize(datetime.now()).astimezone(tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            date = datetime.now()
            time = datetime.now()

        op_fy_date = datetime(2020, 6, 1)
        master_table = []

        for prd in objstockval.product_id:
            sm = self.env['stock.valuation.layer'].search([('company_id', '=', self.env.company.id), ('product_id', '=', prd.id)])
            opening_qty = 0.0
            opening_amt = 0.0
            in_qty = 0.0
            in_amt = 0.0
            out_qty = 0.0
            out_amt = 0.0
            closing_qty = 0.0
            closing_amt = 0.0
            for rec in sm:
                # opening Qty
                if rec.create_date.date() < from_date:
                    opening_qty += rec.quantity
                    opening_amt += rec.value
                    # In Qty

                if from_date <= rec.create_date.date() <= to_date:
                    if rec.quantity > 0:
                        in_qty += rec.quantity
                        in_amt += rec.value
                # Out Qty
                if from_date <= rec.create_date.date() <= to_date:
                    if rec.quantity < 0:
                        out_qty += rec.quantity
                        out_amt += rec.value
                # Closing
                if rec.create_date.date() <= to_date:
                    closing_qty += rec.quantity
                    closing_amt += rec.value

            if closing_qty == 0:
                unit_cost = 0
            else:
                unit_cost = closing_amt / closing_qty
                        
            master_table.append({
                            'product_name': rec.product_id.name,
                            'opening_qty': opening_qty,
                            'opening_amt': opening_amt,
                            'in_qty': in_qty,
                            'in_amt': in_amt,
                            'out_qty': -out_qty,
                            'out_amt': -out_amt,
                            'closing_qty': closing_qty,
                            'unit_cost': unit_cost,
                            'closing_amt': closing_amt,
                        })

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'stock.valuation.layer',
            'docs': master_table,
            'header_date': header_date,
        }
        return docargs