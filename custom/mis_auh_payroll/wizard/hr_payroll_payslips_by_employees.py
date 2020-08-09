# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from datetime import datetime, date, time
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrMisPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _get_hr_tags(self):
        payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        if payslip_run.category_ids:
            return ('category_ids', 'in', payslip_run.category_ids.ids)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_analytic_account(self):
        payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        if payslip_run.analytic_account_id:
            return ('contract_ids.analytic_account_id', '=', payslip_run.analytic_account_id.id)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_analytic_tag_ids(self):
        payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        if payslip_run.analytic_tag_ids:
            return ('contract_ids.x_analytic_tag_ids', 'in', payslip_run.analytic_tag_ids.ids)
        else:
            return ('company_id', '=', self.env.company.id)

    def _get_department_ids(self):
        payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        if payslip_run.hr_department_ids:
            return ('department_id', 'in', payslip_run.hr_department_ids.ids)
        else:
            return ('company_id', '=', self.env.company.id)


    def _get_available_contracts_domain(self):

        return [('contract_ids.state', 'in', ('open', 'close')),
                self._get_hr_tags(), self._get_analytic_account(), self._get_analytic_tag_ids(),
                self._get_department_ids(),
                ('company_id', '=', self.env.company.id)]

