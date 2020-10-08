# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MisAuhPartner1(models.Model):
    _inherit = 'hr.contract'
    _description = 'Added fields for allowance'

    x_house_rent = fields.Float(string="Special Allowance", default=0.00, track_visibility='onchange')
    x_transport = fields.Float(string="Transport", default=0.00, track_visibility='onchange')
    x_other_allowance = fields.Float(string="Allowance", default=0.00, track_visibility='onchange')
    x_net_Salary = fields.Float(string="Net Salary", readonly=True, compute='compute_net_salary', store=True,
                                default=False)
    x_fixed_ot = fields.Float(string="Fixed OT", default=0.00, track_visibility='onchange')
    x_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', copy=True)

    @api.depends('wage', 'x_house_rent', 'x_other_allowance', 'x_fixed_ot')
    def compute_net_salary(self):
        for rec in self:
            rec.x_net_Salary = round(rec.wage+rec.x_house_rent+rec.x_other_allowance+rec.x_fixed_ot, 2)
