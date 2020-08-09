# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import date
from odoo import models, fields

class Employee(models.Model):
    _inherit = "hr.employee"

    
    def get_lwp_type_leave(self, payslip):

        payslip_record = self.env['hr.payslip'].browse(payslip)
        mdays = (payslip_record.date_to - payslip_record.date_from).days
        month_days = mdays + 1
        
        return [month_days]
