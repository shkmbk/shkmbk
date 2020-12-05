from odoo import models, fields, api
from datetime import date
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta


class MbkProperty(models.Model):
    _name = 'mbk.property'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Unit Summary For The Month'
    _order = 'date_to desc'

    name = fields.Char(string='Name', readonly=True, store=True, default='New')
    date = fields.Date('Date', default=fields.Date.to_string(date.today()),
                       states={'draft': [('readonly', False)]}, readonly=True,
                       help="Keep empty to use the period of the validation date.")
    ref = fields.Char(string='Reference', readonly=True, copy=False,
                      states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='As on Date', readonly=True, required=True, copy=False,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
                          states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=3)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, tracking=True, default='draft')
    note = fields.Text(string='Internal Note', readonly=True,
                       states={'draft': [('readonly', False)]})
    total_occupied = fields.Integer(string="Total Occupied Units", compute='_compute_net_closing', store=True,
                                    Default=False)
    total_booked = fields.Integer(string="Total Booked Units", compute='_compute_net_closing', store=True,
                                  Default=False)
    total_vacant = fields.Integer(string="Total Vacant Units", compute='_compute_net_closing', store=True,
                                  Default=False)
    total_units = fields.Integer(string="Total Units", compute='_compute_net_closing', store=True, Default=False)
    total_occupancy_rate = fields.Float(string='Occupancy %', compute='_compute_net_closing', store=True, default=False)
    line_ids = fields.One2many('mbk.property.line', 'property_id',
                               string='Unit Summary Lines', copy=True, readonly=True,
                               states={'draft': [('readonly', False)]})

    def action_load_sheet(self):
        as_on_date = self.date_to
        # as_on_date_str = datetime.strptime(date_to, '%Y-%m-%d').date()
        op_fy_date = datetime(2020, 6, 1).date()

        if not self.ref:
            self.ref = 'Unit Summary for ' + (self.date_to).strftime("%B %Y")
        # delete old unit summary lines
        if self.state in ('draft'):
            self.line_ids.unlink()

        obj_analytic_account = self.env['account.analytic.account'].search(
            [('company_id', '=', 3), ('group_id', '=', 4)], order='id')
        if not obj_analytic_account:
            raise UserError('There are no analytic account found for selected parameters')
        new_lines = self.env['mbk.property.line']

        sl_no = 0
        for rec in obj_analytic_account:
            sl_no += 1
            values = {
                'property_id': self.id,
                'sl_no': sl_no,
                'analytic_account_id': rec.id,
                'occupied_nos': 0,
                'booked_nos': 0,
                'vacant_nos': 0,
                'total_nos': 0,
                'to_date': as_on_date
            }
            new_lines.create(values)
        return new_lines

    def action_property_cancel(self):
        if self.filtered(lambda slip: slip.state == 'post'):
            raise UserError(_("Cannot cancel a property summary is posted."))
        self.write({'state': 'cancel'})

    def action_property_draft(self):
        return self.write({'state': 'draft'})

    def action_post(self):
        if self.name == 'New':
            self.name = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code(
                'mbk.property') or _('New')
        return self.write({'state': 'posted'})

    @api.model
    def create(self, vals):
        vals['state'] = 'draft'
        res = super(MbkProperty, self).create(vals)
        return res

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft') and not self._context.get('force_delete'):
                raise UserError("You cannot delete an entry which has been posted.")
            rec.line_ids.unlink()
        return super(MbkProperty, self).unlink()

    @api.depends('line_ids.total_nos')
    def _compute_net_closing(self):
        for rec in self:
            total_occupied = 0.00
            total_booked = 0.00
            total_vacant = 0.00
            total_units = 0.00
            total_occupancy_rate = 0.00

            for line in rec.line_ids:
                total_occupied += line.occupied_nos
                total_booked += line.booked_nos
                total_vacant += line.vacant_nos
                total_units += line.total_nos
            if total_units > 0:
                total_occupancy_rate += round(total_occupied * 100 / total_units, 2)
            else:
                total_occupancy_rate = 0

            rec.update({
                'total_occupied': total_occupied,
                'total_booked': total_booked,
                'total_vacant': total_vacant,
                'total_units': total_units,
                'total_occupancy_rate': total_occupancy_rate,
            })


class MbkPropertyLine(models.Model):
    _name = 'mbk.property.line'
    _description = 'Property Summary Line'
    _order = 'property_id, sl_no'

    property_id = fields.Many2one('mbk.property', string='Property Summary', required=True, ondelete='cascade',
                                index=True)
    sl_no = fields.Integer(string='Sl', required=True, readonly=True, default=10)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', required=True,
                                          readonly=True, domain="[('company_id', '=', 3), ('group_id', '=', 4)]")
    occupied_nos = fields.Integer(string='Occupied')
    booked_nos = fields.Integer(string='Booked')
    vacant_nos = fields.Integer(string='Vacant')
    total_nos = fields.Integer(string='Total', compute='_get_total', store=True, default=0)
    occupancy_rate = fields.Float(string='Occupancy %', compute='_get_occupancy_rate', store=True, default=False)
    remarks = fields.Char(string='Remarks')
    to_date = fields.Date(string='To Date', readonly=True)

    @api.depends('occupied_nos', 'booked_nos', 'vacant_nos')
    def _get_total(self):
        for rec in self:
            rec.total_nos = rec.occupied_nos + rec.booked_nos + rec.vacant_nos

    @api.depends('occupied_nos', 'total_nos')
    def _get_occupancy_rate(self):
        for rec in self:
            if rec.total_nos > 0:
                rec.occupancy_rate = round(rec.occupied_nos * 100 / rec.total_nos, 2)
            else:
                rec.occupancy_rate = 0
