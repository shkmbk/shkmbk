from odoo import models, fields, api

class MisBank(models.Model):
    _inherit = 'account.journal'

    iban = fields.Char('IBAN')