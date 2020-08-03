# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from datetime import datetime, date, time
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MisCrossinvoiceBillWizard(models.TransientModel):
    _name = 'mis.crossinvoice.wizard'
    _description = 'Cross invoice bill selection'

    def getpartneraccount(self, partnerid):
        rec = self.env['mis.crossinvoice.partner'].search([('partner_id', '=', partnerid)], limit=1)
        if rec:
            return rec.account_id.id
        else:
            return 0

    def _get_available_bill_domain(self, purchasejournalid, transdate, accountid):
        objmvl = self.env['account.move.line'].search([('account_id', '=', accountid)])

        return [('id', 'not in', self._previousmove()), ('id', 'in', objmvl.move_id.ids), ('state', '=', 'posted'), ('type', '=', 'in_invoice') , ('company_id', '=', self.env.company.id), ('journal_id', '=', purchasejournalid), ('invoice_date', '<=', transdate)]

    def _get_bill(self):
        objcrossinv = self.env['mis.crossinvoice'].browse(self.env.context.get('active_id'))
        purchasejournalid = objcrossinv.purchase_journal_id.id
        transdate =objcrossinv.trans_date
        partnerid = objcrossinv.partner_id.id
        accountid = self.getpartneraccount(partnerid)

        return self.env['account.move'].search(self._get_available_bill_domain(purchasejournalid, transdate, accountid))

    def _previousmove(self):

        crossinvoiceids = self.env['mis.crossinvoice.line'].search([]).mapped('move_line_id').move_id
        return crossinvoiceids.ids

    account_move_ids = fields.Many2many('account.move', 'crossinvoice_move_rel', 'move_id', 'cross_id', 'Cross Invoice Bill',
 #                                       domain=lambda self: [('move_id', 'not in', self._previousmove())],
                                    default=lambda self: self._get_bill(), required=True)


    def select_filtered(self):
        self.ensure_one()
        partnerid=0
        salejournalid = 0
        purchasejournalid =0
        if not self.env.context.get('active_id'):
            trans_date = fields.Date.to_date(self.env.context.get('default_trans_date'))
            xref = fields.Char(self.env.context.get('default_ref'))
            salejournalid = self.env.context.get('default_sales_journal_id')
            purchasejournalid = self.env.context.get('default_purchase_journal_id')
            partnerid = self.env.context.get('default_partner_id')
            objcrossinvoice = self.env['mis.crossinvoice'].create({
                'name': 'New',
                'trans_date': trans_date,
                'partner_id': partnerid.id,
                'ref': xref,
            })
        else:
            objcrossinvoice = self.env['mis.crossinvoice'].browse(self.env.context.get('active_id'))
            partnerid = objcrossinvoice.partner_id.id
            salejournalid = objcrossinvoice.sales_journal_id.id
            purchasejournalid = objcrossinvoice.purchase_journal_id.id
            if objcrossinvoice:
                if objcrossinvoice.name =='New':
                    objcrossinvoice.name = self.env['ir.sequence'].with_context(force_company=self.env.company.id).next_by_code(
                        'mis.crossinvoice') or _('New')

        if not self.account_move_ids:
            raise UserError(_("You must select vendor bill(s) to generate cross invoice."))
        objcrossinvoiceline = self.env['mis.crossinvoice.line']
        accountid =self.getpartneraccount(partnerid)
        linecount=0
        for moveids in self.account_move_ids:
            objmoveline = self.env['account.move.line'].search([('move_id', '=', moveids.id), ('exclude_from_invoice_tab', '=', False)])
            for moveline in objmoveline:
                linecount+=1
                values = dict({
                    'move_line_id': moveline.id,
                    'cross_invoice_id': objcrossinvoice.id,
                    'account_id': accountid,
                    'analytic_account_id': moveline.analytic_account_id.id,
                    'analytic_tag_ids': moveline.analytic_tag_ids.ids,
                    'tax_ids':  moveline.tax_ids.ids,
                    'sub_total': moveline.price_subtotal,
                    'tax_amount': moveline.tax_amount,
                    'price_total': moveline.price_total,
                })
                objcrossinvoiceline.create(values)
        objcrossinvoice.totalline=linecount
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mis.crossinvoice',
            'views': [[False, 'form']],
            'res_id': objcrossinvoice.id,
        }
