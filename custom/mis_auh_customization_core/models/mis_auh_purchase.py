# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import time
from datetime import date, datetime
import json
import datetime
from odoo.tools import date_utils

class MisPurchaseOrder(models.Model):
    _inherit = "purchase.order"
    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type', '=', 'purchase')]")
    requested_by= fields.Char(string="Requested By",  required=False, track_visibility='onchange')

    @api.onchange('journal_id')
    def _setanalytic_account(self):
        for frm in self:
            frm.analytic_id = frm.journal_id.analytic_id.id
            for line in self.order_line:
                line.account_analytic_id=frm.journal_id.analytic_id.id

    @api.model
    def create(self, vals):

        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
                posq=''
            if vals['journal_id']:
                journalid = self.env['account.journal'].browse(vals['journal_id'])

                if  journalid.purchase_sequence:
                    if journalid.purchase_sequence_id:
                        posq = self.env['ir.sequence'].next_by_code(journalid.purchase_sequence_id.code, sequence_date=seq_date) or '/'

            if posq:
                vals['name'] =posq
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order', sequence_date=seq_date) or '/'
        return super(MisPurchaseOrder, self).create(vals)

    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_type': 'in_invoice',
            'default_company_id': self.company_id.id,
            'default_purchase_id': self.id,
            'default_journal_id': self.journal_id.id,
            'default_analytic_id': self.journal_id.analytic_id.id,
        }
        # Invoice_ids may be filtered depending on the user. To ensure we get all
        # invoices related to the purchase order, we read them in sudo to fill the
        # cache.
        self.sudo()._read(['invoice_ids'])
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                result['views'] = form_view
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_invoice_origin'] = self.name
        result['context']['default_ref'] = self.partner_ref
        return result

    class MisPurchaseOrderLine(models.Model):
        _inherit = "purchase.order.line"

        @api.onchange('name', 'product_id')
        def _setanalytic_account(self):
            for line in self:
                line.account_analytic_id = line.order_id.analytic_id.id
                if not line.analytic_tag_ids:
                    if line.product_id.invest_analytic_tag_ids:
                        line.analytic_tag_ids=line.product_id.invest_analytic_tag_ids.ids





