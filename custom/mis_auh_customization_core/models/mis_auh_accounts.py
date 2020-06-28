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

class MisAuhAccountType(models.Model):
    _inherit = 'account.account.type'

    account_type_code = fields.Char(string="Account Type Code",  required=True, track_visibility='onchange')

class MisAuhCharofAccount(models.Model):
    _inherit = 'account.account'

    account_old_type_code = fields.Char(string="Old Code",  required=False, track_visibility='onchange')
    account_remark = fields.Char(string="Remarks",  track_visibility='onchange')


    @api.onchange('group_id')
    def _onchangeaccountcode(self):
        if self.group_id:
            isnewcode =True
            if self.code:
                objisfound = self.env['account.account'].search([('code', '=', self.code)])
                if objisfound:
                    isnewcode = False

            if isnewcode:
    #            last_id = self.env['account.account'].search([('user_type_id', '=', self.group_id.account_type_id.id)], order='code desc')[0].code
                objrec = self.env['account.account'].search([('group_id', '=', self.group_id.id)], limit=1, order='code desc')
                if objrec:
                    self.code= int(objrec.code)+1
                else:
                    newcode='00000'+str(int(self.group_id.code_prefix)+1)
                    self.code =newcode[-6:]
            self.user_type_id=self.group_id.account_type_id.id

    @api.onchange('code')
    def onchange_code(self):
        group=False

#        AccountGroup = self.env['account.group']

#        group = False
#        code_prefix = self.code

        # find group with longest matching prefix
#        while code_prefix:
#            matching_group = AccountGroup.search([('code_prefix', '=', code_prefix)], limit=1)
#            if matching_group:
#                group = matching_group

 #               break
 #           code_prefix = code_prefix[:-1]
 #       self.group_id = group


class MisAuhAccountGroup(models.Model):
    _inherit = 'account.group'

    account_type_id = fields.Many2one('account.account.type', required=True, string='Account Type')



