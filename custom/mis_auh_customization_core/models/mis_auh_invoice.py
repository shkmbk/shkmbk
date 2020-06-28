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

class MisAccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('currency_id')
    def _compute_exchage_rate(self):
        for frm in self:
            frm.exchange_rate=frm.currency_id.rate

    @api.onchange('journal_id')
    def _compute_journal_req(self):
        for frm in self:
            frm.is_analytic_account_required = frm.journal_id.is_analytic_account_required
            frm.analytic_id = frm.journal_id.analytic_id.id

    exchange_rate = fields.Float(string="Rate", compute='_compute_exchage_rate', store=True)
    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', store=True)
    is_analytic_account_required=fields.Boolean('Analytic Account Required', store=True,  compute='_compute_journal_req',)

    @api.onchange('analytic_id')
    def _onchange_analytic(self):
        for line in self.line_ids:
            line.analytic_account_id = self.analytic_id


class MisAccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    @api.onchange('account_id')
    def _fillanalytic(self):
       for line in self:
           line.analytic_account_id = line.move_id.analytic_id



    @api.depends('price_total', 'price_subtotal')
    def _compute_tax_amt(self):
       for line in self:
           line.tax_amount=line.price_total-line.price_subtotal
#           if line.move_id.analytic_id:
#               line.parent_analytic_id= line.move_id.analytic_id
#               line.analytic_account_id = line.move_id.analytic_id


    tax_amount = fields.Float(string="Tax Amount", compute='_compute_tax_amt', store=True)
    parent_analytic_id=fields.Many2one('account.analytic.account',  related='move_id.analytic_id', store=True)










