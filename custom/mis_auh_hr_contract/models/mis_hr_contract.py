# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MisAuhPartner1(models.Model):
    _inherit = 'hr.contract'

    x_house_rent = fields.Float(string="House Rent", default=0.00, track_visibility='onchange')
    x_transport = fields.Float(string="Transport", default=0.00, track_visibility='onchange')
    x_other_allowance = fields.Float(string="Other Allowance", default=0.00, track_visibility='onchange')
    x_fixed_ot = fields.Float(string="Fixed OT", default=0.00, track_visibility='onchange')
    x_analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', copy=True)
