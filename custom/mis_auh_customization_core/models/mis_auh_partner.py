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

class MisAuhPartner(models.Model):
    _inherit = 'res.partner'

    partner_code = fields.Char(string="Code",  required=True, track_visibility='onchange')


    @api.onchange('name')
    def _onchange_parrtnername(self):
        if self.name:
            isNotFound = True
            if not self.partner_code:
                objpartner = self.env['res.partner'].search([('partner_code', '!=', False)], order='partner_code desc', limit=1)
                if objpartner:
                    isNotFound=False
                    last_id=objpartner.partner_code
                    strcode = last_id.replace("P", "").replace(" ", "")
                    strcode = "00000" + str(int(strcode) + 1)
                    self.partner_code = "P" + strcode[-5:]
                else:
                    self.partner_code ="P0001"
