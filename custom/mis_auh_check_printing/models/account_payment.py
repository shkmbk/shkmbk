# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import ValidationError, UserError
class account_payment(models.Model):
    _inherit = "account.payment"

    def do_print_checks(self):
        if self:
            #check_layout = self[0].company_id.account_check_printing_layout
            journal_name =self[0].journal_id.name
            # A config parameter is used to give the ability to use this check format even in other countries than US, as not all the localizations have one
            #if check_layout != 'disabled' and (self[0].journal_id.company_id.country_id.code == 'AE' or bool(self.env['ir.config_parameter'].sudo().get_param('account_check_printing_force_ae_format'))):
            #if check_layout != 'disabled' and (self[0].journal_id.company_id.country_id.code == 'AE' or bool(
            #            self.env['ir.config_parameter'].sudo().get_param('account_check_printing_force_ae_format'))):
            self.write({'state': 'sent'})

            if journal_name=='ADIB - 17952837 (CA)':
                check_layout='action_print_check_adib'
            elif journal_name=='ADCB - 265070920012 (CA)':
                check_layout='action_print_check_adcb'
#               else:
#                  check_layout = 'action_print_check_middle'

            return self.env.ref('mis_auh_check_printing.%s' % check_layout).report_action(self)
        return super(account_payment, self).do_print_checks()
