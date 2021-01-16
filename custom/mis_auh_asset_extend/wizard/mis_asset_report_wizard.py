from datetime import timedelta, date, datetime
from odoo.exceptions import UserError
from odoo.tools import date_utils
import xlsxwriter
import base64
from odoo import fields, models, api, _
from io import BytesIO
from pytz import timezone
import pytz


class MisAssetCustomReport(models.TransientModel):
    _name = 'mis.asset.custom.report'

    from_date = fields.Date(string='From Date', required=True)
    to_date = fields.Date(string="To Date", required=True)
    asset_id = fields.Many2one('account.asset', string="Fixed Asset")
    asset_group = fields.Many2one('mis.asset.group', string='Group')
    asset_subgroup = fields.Many2one('mis.asset.subgroup', string='Sub Group')
    asset_brand = fields.Many2one('mis.asset.brand', string='Asset Brand')
    asset_location = fields.Many2one('mis.asset.location', string='Location')
    asset_sublocation = fields.Many2one('mis.asset.sublocation', string='Sub Location',
                                        domain="[('main_location', '=', asset_location)]")
    asset_custodian = fields.Many2one('mis.asset.custodian', string='Custodian')
    asset_area = fields.Many2one('mis.asset.area', string='Area')

    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)

    def _get_asset(self):
        if self.asset_id:
            return ('id', '=', self.asset_id.id)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_group(self):
        if self.asset_group:
            return ('asset_group', '=', self.asset_group.id)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_subgroup(self):
        if self.asset_subgroup:
            return ('asset_subgroup', '=', self.asset_subgroup.id)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_brand(self):
        if self.asset_brand:
            return ('asset_brand', '=', self.asset_brand.id)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_location(self):
        if self.asset_location:
            return ('asset_location', '=', self.asset_location.id)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_sublocation(self):
        if self.asset_sublocation:
            return ('asset_sublocation', '=', self.asset_sublocation.id)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_custtodian(self):
        if self.asset_custodian:
            return ('asset_custodian', '=', self.asset_custodian.id)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_area(self):
        if self.asset_area:
            return ('asset_area', '=', self.asset_area.id)
        else:
            return ('company_id', '=', self.env.company.id)

    def _getdomainfilter(self):
        return [self._get_asset(), self._get_group(), self._get_subgroup(), self._get_brand(),
                self._get_location(), self._get_sublocation(),
                self._get_custtodian(), self._get_area(), ('acquisition_date', '<=', self.to_date),
                ('company_id', '=', self.env.company.id), ('asset_type', '=', 'purchase'), ('state', 'not in', ['draft', 'model'])
                ]

    def print_asset_xlsx(self):
        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))

        objasset = self.env['account.asset'].search(self._getdomainfilter())

        if not objasset:
            raise UserError(_('There are no Asset found for selected parameters'))

        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            date = pytz.utc.localize(datetime.now()).astimezone(tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            date = datetime.now()
            time = datetime.now()
        date_string = self.to_date.strftime("%B-%y")

        report_name = 'AssetReport_' + date.strftime("%y%m%d%H%M%S")
        filename = '%s %s' % (report_name, date_string)

        pre_cls_date = self.from_date - timedelta(days=1)
        op_fy_date = datetime(2020, 6, 1)

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
        wbf['content_float_border_bg'] = workbook.add_format(
            {'align': 'right', 'num_format': '#,##0.00', 'bold': 1, 'bg_color': '#E1E1E1'})
        wbf['content_float_border_bg'].set_top()
        wbf['content_float_border_bg'].set_bottom()
        wbf['content_float_border_bg'].set_left()
        wbf['content_float_border_bg'].set_right()

        worksheet = workbook.add_worksheet(report_name)
        count = 0
        col = 0
        column_width = 6
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Sl. No.', wbf['content_border_bg'])
        col += 1
        column_width = 12
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Asset Code', wbf['content_border_bg'])
        col += 1
        column_width = 43
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Asset', wbf['content_border_bg'])
        col += 1
        column_width = 30
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Fixed Asset', wbf['content_border_bg'])
        col += 1
        column_width = 13
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Purchase Date', wbf['content_border_bg'])
        col += 1
        column_width = 10
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Qty', wbf['content_border_bg'])
        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Cost', wbf['content_border_bg'])
        col += 1
        column_width = 18
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Purchase Value', wbf['content_border_bg'])
        """col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Addition', wbf['content_border_bg'])
        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Disposal', wbf['content_border_bg'])
        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Closing Cost', wbf['content_border_bg'])
        
        """
        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, ' Salvage', wbf['content_border_bg'])

        col += 1
        column_width = 16
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Depreciable Value', wbf['content_border_bg'])

        col += 1
        column_width = 13
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Total Duration', wbf['content_border_bg'])

        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Depr. Opening', wbf['content_border_bg'])

        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'Depr. for Period', wbf['content_border_bg'])

        col += 1
        column_width = 14
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, ' Accum. depr.', wbf['content_border_bg'])

        col += 1
        column_width = 16
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'NBV ' + pre_cls_date.strftime("%d-%m-%Y"), wbf['content_border_bg'])

        col += 1
        column_width = 16
        worksheet.set_column(col, col, column_width)
        worksheet.write(count, col, 'NBV ' + self.to_date.strftime("%d-%m-%Y"), wbf['content_border_bg'])

        for rec in objasset:
            count += 1
            col = 0
            purchase_value = 0.0
            if rec.is_opening == True:
                purchase_date = rec.asset_purchase_date
                purchase_value = rec.asset_purchase_amount
                depreciable_value = purchase_value - rec.salvage_value
                duration = rec.op_duration
            else:
                purchase_date = rec.acquisition_date
                purchase_value = rec.original_value
                depreciable_value = rec.value_residual
                duration = rec.method_number

            # SEQ
            worksheet.write(count, col, count, wbf['content_border'])
            col += 1
            # Asset Code
            worksheet.write(count, col, rec.asset_code, wbf['content_border'])
            # Name
            col += 1
            worksheet.write(count, col, rec.name, wbf['content_border'])
            # Fixed Asset
            col += 1
            worksheet.write(count, col, rec.account_asset_id.name, wbf['content_border'])
            # Purchase Date
            col += 1
            if purchase_date:
                worksheet.write(count, col, purchase_date.strftime("%d-%m-%Y"), wbf['content_border'])
            else:
                worksheet.write(count, col, '', wbf['content_border'])
            # QTY
            col += 1
            worksheet.write(count, col, rec.asset_qty, wbf['content_border'])
            # Cost
            col += 1

            purchased_cost = rec.asset_cost
            worksheet.write(count, col, purchased_cost, wbf['content_float_border'])
            # Opening Balance
            col += 1
            worksheet.write(count, col, purchase_value, wbf['content_float_border'])
            # Addition
            """col += 1
            worksheet.write(count, col, 0.0, wbf['content_float_border'])
            # Disposal
            col += 1
            worksheet.write(count, col, 0.0, wbf['content_float_border'])
            # Closing Cost
            col += 1
            closing_cost = purchased_cost
            worksheet.write(count, col, closing_cost, wbf['content_float_border'])
            
            """
            # SALVAGE
            col += 1
            worksheet.write(count, col, rec.salvage_value, wbf['content_float_border'])
            # DEPRECIABLE VALUE
            col += 1
            worksheet.write(count, col, depreciable_value, wbf['content_float_border'])

            # Total Duration
            strmy = 'Months'
            if rec.method_period == 1:
                strmy = 'Years'
            else:
                strmy = 'Months'
            col += 1
            worksheet.write(count, col, str(duration) + ' ' + strmy, wbf['content_border'])

            dep_current_opening = 0.00
            depreciation_period = 0.00
            net_current_av = 0.00
            net_current_op_av = 0.00

            objmove = self.env['account.move'].search(
                [('asset_id', '=', rec.id), ('state', '=', 'posted'), ('date', '<=', self.to_date)], order='date')
            for mvrec in objmove:
                if mvrec.date >= self.from_date:
                    for line in mvrec.line_ids:
                        if line.account_id.user_type_id.id == 16:
                            depreciation_period += line.debit - line.credit
                        if line.account_id.user_type_id.id == 8:
                            net_current_av += line.debit - line.credit
                else:
                    for line in mvrec.line_ids:
                        if line.account_id.user_type_id.id == 16:
                            dep_current_opening += line.debit - line.credit
                        if line.account_id.user_type_id.id == 8:
                            net_current_op_av += line.debit - line.credit

            # Depreciation Opening
            col += 1
            dep_opening = (purchase_value - rec.original_value) + dep_current_opening
            worksheet.write(count, col, dep_opening, wbf['content_float_border'])
            # Depreciation for Period
            col += 1
            worksheet.write(count, col, depreciation_period, wbf['content_float_border'])
            # Accumated Depreciation
            col += 1
            # acc_depreciation_amount=self._getSum(rec.id,0,1,self.from_date,self.to_date)
            acc_depreciation_amount = dep_opening + depreciation_period
            worksheet.write(count, col, acc_depreciation_amount, wbf['content_float_border'])
            # Previous Closing NBV Value
            col += 1
            fromdate_value = rec.original_value + net_current_op_av
            worksheet.write(count, col, fromdate_value, wbf['content_float_border'])
            # To Date NBA Value
            col += 1
            todate_value = rec.original_value + net_current_op_av + net_current_av
            worksheet.write(count, col, todate_value, wbf['content_float_border'])

        count += 2
        # SUMMARY
        worksheet.merge_range('A%s:C%s' % (count, count), 'Total', wbf['content_float_border_bg'])
        col = 3
        worksheet.write(count - 1, col, "", wbf['content_border_bg'])
        col += 1
        worksheet.write(count - 1, col, "", wbf['content_border_bg'])
        col += 1
        worksheet.write_formula('F%s' % (count), '=SUM(F2:F%s)' % (count - 1), wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, "", wbf['content_border_bg'])
        col += 1
        worksheet.write_formula('H%s' % (count), '=SUM(H2:H%s)' % (count - 1), wbf['content_float_border_bg'])
        col += 1
        worksheet.write_formula('I%s' % (count), '=SUM(I2:I%s)' % (count - 1), wbf['content_float_border_bg'])
        col += 1
        worksheet.write_formula('J%s' % (count), '=SUM(J2:J%s)' % (count - 1), wbf['content_float_border_bg'])
        col += 1
        worksheet.write(count - 1, col, "", wbf['content_border_bg'])
        col += 1
        worksheet.write_formula('L%s' % (count), '=SUM(L2:L%s)' % (count - 1), wbf['content_float_border_bg'])
        col += 1
        worksheet.write_formula('M%s' % (count), '=SUM(M2:M%s)' % (count - 1), wbf['content_float_border_bg'])
        col += 1
        worksheet.write_formula('N%s' % (count), '=SUM(N2:N%s)' % (count - 1), wbf['content_float_border_bg'])
        col += 1
        worksheet.write_formula('O%s' % (count), '=SUM(O2:O%s)' % (count - 1), wbf['content_float_border_bg'])
        col += 1
        worksheet.write_formula('P%s' % (count), '=SUM(P2:P%s)' % (count - 1), wbf['content_float_border_bg'])

        workbook.close()
        out = base64.encodebytes(fp.getvalue())
        self.write({'datas': out, 'datas_fname': filename})
        fp.close()
        filename += '%2Exlsx'

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/?model=' + self._name + '&id=' + str(
                self.id) + '&field=datas&download=true&filename=' + filename,
        }
