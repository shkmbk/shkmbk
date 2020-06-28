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

class MisAuhJournal(models.Model):
    _inherit = 'account.journal'

    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    is_analytic_account_required = fields.Boolean(string='Analytic Account Required in Invoice / Bill')
    sale_sequence = fields.Boolean(string='Dedicated Sale Sequence', default=False)
    sale_sequence_id = fields.Many2one('ir.sequence', string='Sale Sequence', copy=False)
    purchase_sequence = fields.Boolean(string='Dedicated Purchase Sequence', default=False )
    purchase_sequence_id = fields.Many2one('ir.sequence', string='Purchase Sequence', copy=False)
