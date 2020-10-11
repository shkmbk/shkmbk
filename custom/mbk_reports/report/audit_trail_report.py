from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from pytz import timezone
import pytz


class Audit_Trail_Report(models.AbstractModel):
    _name = 'report.mbk_reports.report_audit_trail'
    _description = "Audit Trail Report"

    def _get_report_values(self, docids, data=None):
        self.env['ir.rule'].clear_cache()
        from_date = data['from_date']
        to_date = data['to_date']
        user_id = data['user_id']
        is_include_auto = data['is_include_auto']
        header_period = data['header_period']

        cid = self.env.company.id

        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))
        if user_id:
            obj_accounts = self.env['account.move'].search([('write_date', '>=', from_date), ('write_date', '<=', to_date), ('auto_post', '=', is_include_auto), '|', ('create_uid', '=', user_id), ('write_uid', '=', user_id)])
            obj_sales_order = self.env['sale.order'].search([('write_date', '>=', from_date), ('write_date', '<=', to_date), '|', ('create_uid', '=', user_id), ('write_uid', '=', user_id)])
            obj_purchase_order = self.env['purchase.order'].search([('write_date', '>=', from_date), ('write_date', '<=', to_date), '|', ('create_uid', '=', user_id), ('write_uid', '=', user_id)])
            obj_statement = self.env['account.bank.statement'].search([('write_date', '>=', from_date), ('write_date', '<=', to_date), '|', ('create_uid', '=', user_id), ('write_uid', '=', user_id)])
        else:
            obj_accounts = self.env['account.move'].search([('write_date', '>=', from_date), ('write_date', '<=', to_date), ('auto_post', '=', is_include_auto)])
            obj_sales_order = self.env['sale.order'].search([('write_date', '>=', from_date), ('write_date', '<=', to_date)])
            obj_purchase_order = self.env['purchase.order'].search([('write_date', '>=', from_date), ('write_date', '<=', to_date)])
            obj_statement = self.env['account.bank.statement'].search([('write_date', '>=', from_date), ('write_date', '<=', to_date)])

        if not obj_accounts:
            raise UserError('There are no records found for selected parameters')

        master_table = []

        for rec in obj_accounts:
            wurl = "/web#id=" + str(rec.id) + "&action=205&model=account.move&view_type=form&cids="+str(cid)+"&menu_id=255"
            master_table.append({
                'doc_group': 'Accounts',
                'doc_type': rec.journal_id.name,
                'doc_no': rec.name,
                'doc_date': rec.date.strftime("%d-%m-%Y"),
                'ref': rec.ref,
                'ref_date': rec.invoice_date,
                'partner_id': rec.partner_id.name,
                'amount': rec.amount_total,
                'status': rec.state,
                'narration': rec.narration,
                'create_user': rec.create_uid.name,
                'update_user': rec.write_uid.name,
                'create_time': rec.create_date.strftime("%d-%m-%Y %H:%M"),
                'update_time': rec.write_date.strftime("%d-%m-%Y %H:%M"),
                'wurl': wurl,
            })
        for rec in obj_sales_order:
            wurl = "/web#id=" + str(rec.id) + "&action=292&model=sale.order&view_type=form&cids="+str(cid)+"&menu_id=171"
            master_table.append({
                'doc_group': 'Sales',
                'doc_type': 'Sales Order',
                'doc_no': rec.name,
                'doc_date': rec.date.strftime("%d-%m-%Y"),
                'ref': rec.client_order_ref,
                'ref_date': rec.date.strftime("%d-%m-%Y"),
                'partner_id': rec.partner_id.name,
                'amount': rec.amount_total,
                'status': rec.state,
                'narration': rec.note,
                'create_user': rec.create_uid.name,
                'update_user': rec.write_uid.name,
                'create_time': rec.create_date.strftime("%d-%m-%Y %H:%M"),
                'update_time': rec.write_date.strftime("%d-%m-%Y %H:%M"),
                'wurl': wurl,
            })
        for rec in obj_purchase_order:
            wurl = "/web#id=" + str(rec.id) + "&action=319&model=purchase.order&view_type=form&cids="+str(cid)+"&menu_id=199"
            if rec.date_approve:
                po_date = rec.date_approve.strftime("%d-%m-%Y")
            else:
                po_date = rec.date_order.strftime("%d-%m-%Y")
            master_table.append({
                'doc_group': 'Purchase',
                'doc_type': 'Purchase Order',
                'doc_no': rec.name,
                'doc_date': po_date,
                'ref': rec.partner_ref,
                'ref_date': rec.date_order.strftime("%d-%m-%Y"),
                'partner_id': rec.partner_id.name,
                'amount': rec.amount_total,
                'status': rec.state,
                'narration': rec.notes,
                'create_user': rec.create_uid.name,
                'update_user': rec.write_uid.name,
                'create_time': rec.create_date.strftime("%d-%m-%Y %H:%M"),
                'update_time': rec.write_date.strftime("%d-%m-%Y %H:%M"),
                'wurl': wurl,
            })
        for rec in obj_statement:
            wurl = "/web#id=" + str(rec.id) + "&action=240&model=account.bank.statement&view_type=form&cids="+str(cid)+"&menu_id=255"
            master_table.append({
                'doc_group': 'Statement',
                'doc_type': 'Reconciliation',
                'doc_no': rec.name,
                'doc_date': rec.date.strftime("%d-%m-%Y"),
                'ref': '',
                'ref_date': rec.date.strftime("%d-%m-%Y"),
                'partner_id': rec.journal_id.id,
                'amount': rec.balance_start-rec.balance_end,
                'status': rec.state,
                'narration': '',
                'create_user': rec.create_uid.name,
                'update_user': rec.write_uid.name,
                'create_time': rec.create_date.strftime("%d-%m-%Y %H:%M"),
                'update_time': rec.write_date.strftime("%d-%m-%Y %H:%M"),
                'wurl': wurl,
            })


        if not obj_accounts:
            raise UserError('There are no records found for selected parameters')
        # master_table.sort(key=lambda g: (g['audit_trail_amount'], g['eligible_days']), reverse=True)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'account.move',
            'docs': master_table,
            'header_period': header_period,
        }
        return docargs
