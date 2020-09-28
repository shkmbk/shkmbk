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


class MbkVATReturn(models.TransientModel):
    _name = 'mbk.wizard.report.vat_return'
    _description = 'VAT Return Format'

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'UTC'))

    from_date = fields.Date(string='From Date', default='2020-07-01', required=True)
    to_date = fields.Date(string="To Date", default='2020-07-31', required=True)
    analytic_id = fields.Many2one('account.analytic.account', "Analytic Account")

    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)

    def _get_analytic(self):
        if self.analytic_id:
            return ('analytic_id', '=', self.analytic_id.id)
        else:
            return (1, '=', 1)

    def _getdomainfilter(self):
        return [('date', '>=', self.from_date), ('date', '<=', self.to_date), self._get_analytic(),
                ('company_id', '=', self.env.company.id), ('parent_state', '=', 'posted'),
                ('tax_ids.id', '!=', False)
                ]

    def print_vat_return_xls(self):

        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))

        obj_invoice = self.env['account.move.line'].search(self._getdomainfilter())

        if not obj_invoice:
            raise UserError(_('There are no bills found for selected parameters'))

        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            date = pytz.utc.localize(datetime.now()).astimezone(tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            date = datetime.now()
            time = datetime.now()
        date_string = self.to_date.strftime("%B-%y")
        date_from_string = self.from_date.strftime("%B-%y")
        date_to_string = self.to_date.strftime("%B-%y")

        report_name = 'Inward Supplies'
        # filename = '%s %s' % (report_name, date_string)
        filename = 'VAT Return Format ('+date_from_string+'-'+date_to_string+') '+date.strftime("%y%m%d%H%M%S")

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

        wbf['content_date_border'] = workbook.add_format({'align': 'center', 'num_format': 'dd/mm/yyyy'})
        wbf['content_date_border'].set_top()
        wbf['content_date_border'].set_bottom()
        wbf['content_date_border'].set_left()
        wbf['content_date_border'].set_right()

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

        worksheet1 = workbook.add_worksheet('Inward Supplies')
        worksheet3 = workbook.add_worksheet('Outward Supplies')
        worksheet2 = workbook.add_worksheet('Debit Note')
        worksheet4 = workbook.add_worksheet('Credit Note')
        worksheet5 = workbook.add_worksheet('Errors')

        count = 0

        # Report Heading
        col = 0
        column_width = 7
        worksheet1.set_column(col, col, column_width)
        worksheet1.write(count, col, 'Sl. No.', wbf['content_border_bg'])
        worksheet2.set_column(col, col, column_width)
        worksheet2.write(count, col, 'Sl. No.', wbf['content_border_bg'])
        worksheet3.set_column(col, col, column_width)
        worksheet3.write(count, col, 'Sl. No.', wbf['content_border_bg'])
        worksheet4.set_column(col, col, column_width)
        worksheet4.write(count, col, 'Sl. No.', wbf['content_border_bg'])
        worksheet5.set_column(col, col, column_width)
        worksheet5.write(count, col, 'Sl. No.', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 72)
        worksheet1.write(count, col, 'Tax Invoice No.', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 18)
        worksheet2.write(count, col, 'Debit Note No', wbf['content_border_bg'])
        worksheet3.set_column(col, col, 15)
        worksheet3.write(count, col, 'Invoice Date.', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 18)
        worksheet4.write(count, col, 'Credit Note No.', wbf['content_border_bg'])
        worksheet5.set_column(col, col, 20)
        worksheet5.write(count, col, 'Document No.', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 15)
        worksheet1.write(count, col, 'Tax Invoice Date', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 15)
        worksheet2.write(count, col, 'Debit Note Date', wbf['content_border_bg'])
        worksheet3.set_column(col, col, 20)
        worksheet3.write(count, col, 'Invoice No.', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 15)
        worksheet4.write(count, col, 'Credit Note Date', wbf['content_border_bg'])
        worksheet5.set_column(col, col, 15)
        worksheet5.write(count, col, 'Document Date', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 15)
        worksheet1.write(count, col, 'Posting Date', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 25)
        worksheet2.write(count, col, 'Original Invoice No.', wbf['content_border_bg'])
        worksheet3.set_column(col, col, 20)
        worksheet3.write(count, col, 'Type of Transaction', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 25)
        worksheet4.write(count, col, 'Original Invoice No.', wbf['content_border_bg'])
        worksheet5.set_column(col, col, 20)
        worksheet5.write(count, col, 'Amount', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 22)
        worksheet1.write(count, col, 'Accounting Voucher No.', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 16)
        worksheet2.write(count, col, 'Original Invoice date', wbf['content_border_bg'])
        worksheet3.set_column(col, col, 25)
        worksheet3.write(count, col, 'Customer', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 16)
        worksheet4.write(count, col, 'Original Invoice date', wbf['content_border_bg'])
        worksheet5.set_column(col, col, 14)
        worksheet5.write(count, col, 'Tax ID', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 25)
        worksheet1.write(count, col, 'Supplier', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 17)
        worksheet2.write(count, col, 'Original posting date', wbf['content_border_bg'])
        worksheet3.set_column(col, col, 17)
        worksheet3.write(count, col, 'TRN', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 20)
        worksheet4.write(count, col, 'Original place of supply', wbf['content_border_bg'])
        worksheet5.set_column(col, col, 15)
        worksheet5.write(count, col, 'Tax Amount', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 18)
        worksheet1.write(count, col, 'TRN', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 30)
        worksheet2.write(count, col, 'Original accounting invoice No.', wbf['content_border_bg'])
        worksheet3.set_column(col, col, 50)
        worksheet3.write(count, col, 'Invoice Description', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 30)
        worksheet4.write(count, col, 'Original accounting invoice No.', wbf['content_border_bg'])
        worksheet5.set_column(col, col, 14)
        worksheet5.write(count, col, 'Net Amount', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 45)
        worksheet1.write(count, col, 'Invoice Description', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 14)
        worksheet2.write(count, col, 'Type of Transaction', wbf['content_border_bg'])
        worksheet3.set_column(col, col, 14)
        worksheet3.write(count, col, 'Amount', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 14)
        worksheet4.write(count, col, 'Type of Transaction', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 17)
        worksheet1.write(count, col, 'Type of Transaction', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 30)
        worksheet2.write(count, col, 'Supplier', wbf['content_border_bg'])
        worksheet3.set_column(col, col, 12)
        worksheet3.write(count, col, 'VATRate', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 25)
        worksheet4.write(count, col, 'Customer', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 7)
        worksheet1.write(count, col, 'Qty', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 18)
        worksheet2.write(count, col, 'TRN', wbf['content_border_bg'])
        worksheet3.set_column(col, col, 18)
        worksheet3.write(count, col, 'VAT Amount', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 18)
        worksheet4.write(count, col, 'TRN', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 12)
        worksheet1.write(count, col, 'Excluding VAT', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 12)
        worksheet2.write(count, col, 'Amount', wbf['content_border_bg'])
        worksheet3.set_column(col, col, 20)
        worksheet3.write(count, col, 'Document Type', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 12)
        worksheet4.write(count, col, 'Amount', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 8)
        worksheet1.write(count, col, 'Discount', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 12)
        worksheet2.write(count, col, 'VAT Rate', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 12)
        worksheet4.write(count, col, 'VAT Rate', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 12)
        worksheet1.write(count, col, 'Amount', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 12)
        worksheet2.write(count, col, 'VAT Amount', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 12)
        worksheet4.write(count, col, 'VAT Amount', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 9)
        worksheet1.write(count, col, 'VAT Rate', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 12)
        worksheet2.write(count, col, 'Net Amount', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 12)
        worksheet4.write(count, col, 'VAT Amount', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 12)
        worksheet1.write(count, col, 'VAT Amount', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 14)
        worksheet2.write(count, col, 'Eligibility of ITC', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 14)
        worksheet4.write(count, col, 'Net Amount', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 14)
        worksheet1.write(count, col, 'Eligibility of ITC', wbf['content_border_bg'])
        worksheet2.set_column(col, col, 20)
        worksheet2.write(count, col, 'Document Type', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 14)
        worksheet4.write(count, col, 'Eligibility of ITC', wbf['content_border_bg'])
        col += 1
        worksheet1.set_column(col, col, 20)
        worksheet1.write(count, col, 'Document Type', wbf['content_border_bg'])
        worksheet4.set_column(col, col, 20)
        worksheet4.write(count, col, 'Document Type', wbf['content_border_bg'])

        out_inv_count = 0
        out_cn_count = 0
        in_inv_count = 0
        in_dn_count = 0
        err_count = 0

        for rec in obj_invoice:
            tax_names = ''
            for t in rec.tax_ids:
                if tax_names == '':
                    tax_names += t.name
                else:
                    tax_names += ', ' + t.name

            if rec.tax_ids.id == 19:
                if rec.move_id.type == 'out_refund':
                    in_dn_count += 1
                    # SEQ
                    worksheet2.write(in_dn_count, 0, in_dn_count, wbf['content_border'])
                    worksheet2.write(in_dn_count, 1, rec.move_id.name, wbf['content_border'])
                    worksheet2.write(in_dn_count, 2, rec.move_id.date, wbf['content_date_border'])
                    worksheet2.write(in_dn_count, 3, rec.move_id.ref, wbf['content_border'])
                    worksheet2.write(in_dn_count, 4, rec.move_id.invoice_date, wbf['content_date_border'])
                    worksheet2.write(in_dn_count, 5, rec.move_id.invoice_date, wbf['content_date_border'])
                    worksheet2.write(in_dn_count, 6, rec.move_id.ref, wbf['content_border'])
                    worksheet2.write(in_dn_count, 7, 'Taxable Supply', wbf['content_border'])
                    worksheet2.write(in_dn_count, 8, rec.move_id.partner_id.name, wbf['content_border'])
                    worksheet2.write(in_dn_count, 9, rec.move_id.partner_id.vat, wbf['content_border'])
                    worksheet2.write(in_dn_count, 10, rec.price_subtotal, wbf['content_float_border'])
                    worksheet2.write(in_dn_count, 11, tax_names, wbf['content_border'])
                    worksheet2.write(in_dn_count, 12, rec.price_total - rec.price_subtotal, wbf['content_float_border'])
                    worksheet2.write(in_dn_count, 13, rec.price_total, wbf['content_float_border'])
                    worksheet2.write(in_dn_count, 14, 'TRUE', wbf['content_border'])
                    worksheet2.write(in_dn_count, 15, rec.move_id.journal_id.name, wbf['content_border'])
                else:
                    in_inv_count += 1
                    # SEQ
                    worksheet1.write(in_inv_count, 0, in_inv_count, wbf['content_border'])
                    worksheet1.write(in_inv_count, 1, rec.move_id.ref, wbf['content_border'])
                    worksheet1.write(in_inv_count, 2, rec.move_id.invoice_date, wbf['content_date_border'])
                    worksheet1.write(in_inv_count, 3, rec.move_id.date, wbf['content_date_border'])
                    worksheet1.write(in_inv_count, 4, rec.move_id.name, wbf['content_border'])
                    worksheet1.write(in_inv_count, 5, rec.move_id.partner_id.name, wbf['content_border'])
                    worksheet1.write(in_inv_count, 6, rec.move_id.partner_id.vat, wbf['content_border'])
                    worksheet1.write(in_inv_count, 7, rec.name, wbf['content_border'])
                    worksheet1.write(in_inv_count, 8, 'Taxable Supply', wbf['content_border'])
                    worksheet1.write(in_inv_count, 9, rec.quantity, wbf['content_border'])
                    worksheet1.write(in_inv_count, 10, rec.price_subtotal, wbf['content_float_border'])
                    worksheet1.write(in_inv_count, 11, rec.discount, wbf['content_float_border'])
                    worksheet1.write(in_inv_count, 12, rec.price_subtotal, wbf['content_float_border'])
                    worksheet1.write(in_inv_count, 13, tax_names, wbf['content_border'])
                    worksheet1.write(in_inv_count, 14, rec.price_total - rec.price_subtotal, wbf['content_float_border'])
                    worksheet1.write(in_inv_count, 15, 'TRUE', wbf['content_border'])
                    worksheet1.write(in_inv_count, 16, rec.move_id.journal_id.name, wbf['content_border'])

            if rec.tax_ids.id == 2:
                if rec.move_id.type == 'out_invoice':
                    out_inv_count += 1
                    # SEQ
                    worksheet3.write(out_inv_count, 0, out_inv_count, wbf['content_border'])
                    worksheet3.write(out_inv_count, 1, rec.move_id.invoice_date, wbf['content_date_border'])
                    worksheet3.write(out_inv_count, 2, rec.move_id.name, wbf['content_border'])
                    worksheet3.write(out_inv_count, 3, 'Taxable Supply', wbf['content_border'])
                    worksheet3.write(out_inv_count, 4, rec.move_id.partner_id.name, wbf['content_border'])
                    worksheet3.write(out_inv_count, 5, rec.move_id.partner_id.vat, wbf['content_border'])
                    worksheet3.write(out_inv_count, 6, rec.name, wbf['content_border'])
                    worksheet3.write(out_inv_count, 7, rec.price_subtotal, wbf['content_float_border'])
                    worksheet3.write(out_inv_count, 8, tax_names, wbf['content_border'])
                    worksheet3.write(out_inv_count, 9, rec.price_total - rec.price_subtotal, wbf['content_float_border'])
                    worksheet3.write(out_inv_count, 10, rec.move_id.journal_id.name, wbf['content_border'])
                else:
                    out_cn_count += 1
                    # SEQ
                    worksheet4.write(out_cn_count, 0, out_cn_count, wbf['content_border'])
                    worksheet4.write(out_cn_count, 1, rec.move_id.name, wbf['content_border'])
                    worksheet4.write(out_cn_count, 2, rec.move_id.invoice_date, wbf['content_date_border'])
                    worksheet4.write(out_cn_count, 3, rec.move_id.ref, wbf['content_border'])
                    worksheet4.write(out_cn_count, 4, rec.move_id.invoice_date, wbf['content_date_border'])
                    worksheet4.write(out_cn_count, 5, rec.move_id.fiscal_position_id.name, wbf['content_date_border'])
                    worksheet4.write(out_cn_count, 6, 'Taxable Supply', wbf['content_border'])
                    worksheet4.write(out_cn_count, 7, rec.move_id.partner_id.name, wbf['content_border'])
                    worksheet4.write(out_cn_count, 8, rec.move_id.partner_id.vat, wbf['content_border'])
                    worksheet4.write(out_cn_count, 9, rec.price_subtotal, wbf['content_float_border'])
                    worksheet4.write(out_cn_count, 10, tax_names, wbf['content_border'])
                    worksheet4.write(out_cn_count, 11, rec.price_total - rec.price_subtotal, wbf['content_float_border'])
                    worksheet4.write(out_cn_count, 12, rec.price_total, wbf['content_float_border'])
                    worksheet4.write(out_cn_count, 13, rec.move_id.journal_id.name, wbf['content_border'])
            if rec.tax_ids.id not in [48, 49, 2, 19]:
                err_count += 1
                # SEQ
                worksheet5.write(err_count, 0, err_count, wbf['content_border'])
                worksheet5.write(err_count, 1, rec.move_id.name, wbf['content_border'])
                worksheet5.write(err_count, 2, rec.date, wbf['content_date_border'])
                worksheet5.write(err_count, 3, rec.price_subtotal, wbf['content_border'])
                worksheet5.write(err_count, 4, tax_names, wbf['content_border'])
                worksheet5.write(err_count, 5, rec.price_total - rec.price_subtotal, wbf['content_border'])
                worksheet5.write(err_count, 6, rec.price_total, wbf['content_border'])

        worksheet1.merge_range('A%s:J%s' % (in_inv_count+2, in_inv_count+2), 'Total', wbf['content_border_bg_total'])
        worksheet1.write_formula('K%s' % (in_inv_count+2), '=SUM(K2:K%s)' % (in_inv_count+1), wbf['content_border_bg_total'])
        worksheet1.write_formula('L%s' % (in_inv_count+2), '=SUM(L2:L%s)' % (in_inv_count+1), wbf['content_border_bg_total'])
        worksheet3.write(in_inv_count + 1, 13, '', wbf['content_border_bg_total'])
        worksheet3.write(in_inv_count+1, 15, '', wbf['content_border_bg_total'])
        worksheet3.write(in_inv_count+1, 16, '', wbf['content_border_bg_total'])

        worksheet3.merge_range('A%s:G%s' % (out_inv_count+2, out_inv_count+2), 'Total', wbf['content_border_bg_total'])
        worksheet3.write_formula('H%s' % (out_inv_count+2), '=SUM(H2:K%s)' % (out_inv_count+1), wbf['content_border_bg_total'])
        worksheet3.write_formula('J%s' % (out_inv_count+2), '=SUM(J2:L%s)' % (out_inv_count+1), wbf['content_border_bg_total'])
        worksheet3.write(out_inv_count+1, 8, '', wbf['content_border_bg_total'])
        worksheet3.write(out_inv_count+1, 10, '', wbf['content_border_bg_total'])

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
