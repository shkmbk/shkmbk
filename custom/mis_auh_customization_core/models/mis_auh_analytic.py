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

class MisAuhAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    analytic_tag_group = fields.Many2one('mis.analytic.tag.group', string='Group')


class MisAuhAnalyticTagGroup(models.Model):
    _name = 'mis.analytic.tag.group'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Group",  required=True, track_visibility='onchange')

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Analytc Tag Group name already exists !"),
    ]