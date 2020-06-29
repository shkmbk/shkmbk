from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Mis_Auh_AccountMoveLine(models.Model):
    _inherit = 'account.move.line'



    acc_group_id = fields.Many2one('account.group', related='account_id.group_id', string="Account Group", store=True)
    acc_type_id = fields.Many2one('account.account.type', related='account_id.user_type_id', string="Account Type", store=True)