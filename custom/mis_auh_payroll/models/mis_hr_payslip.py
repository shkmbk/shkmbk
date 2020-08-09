# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MisHrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super(MisHrPayslip, self).action_payslip_done()
        for line in self.move_id.line_ids:
            if line.analytic_account_id:
                line.write({
                    'analytic_tag_ids': [(6, 0,self.contract_id.x_analytic_tag_ids.ids)]
                    })
        return res