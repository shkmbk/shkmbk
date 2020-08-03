# -*- coding: utf-8 -*-
#
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
class MisAuhCrossInvoice(models.Model):
    _name = 'mis.crossinvoice'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description ='Cross Invoice to Sister Companies'

    def getpurchasejournal(self):
        rec = self.env['mis.crossinvoice.journal'].search([])
        pjnllist = []
        for r in rec:
            pjnllist.append(r.purchase_journal_id.id)
        return pjnllist

    def getsalesjournal(self):
        rec = self.env['mis.crossinvoice.journal'].search([])
        sjnllist = []
        for r in rec:
            sjnllist.append(r.sales_journal_id.id)
        return sjnllist

    @api.onchange('sales_journal_id')
    def _onchange_journal_id(self):
        recjnr = self.env['mis.crossinvoice.journal'].search([('sales_journal_id', '=', self.sales_journal_id.id)])

        if recjnr:
            self.purchase_journal_id=recjnr.purchase_journal_id.id


    state = fields.Selection([
        ('draft', 'New'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    name = fields.Char('Name', default ='New')
    partner_id = fields.Many2one('res.partner', ondelete="cascade", required=True, string='Partner')
    ref = fields.Char('Reference', required=True)
    trans_date=fields.Date(string='Date')
#    purchase_journal_id = fields.Many2one('account.journal', string='Purchase Journal', readonly=True, store=True, domain = lambda self: [('id', 'in', self.getpurchasejournal())], required=True)
    purchase_journal_id = fields.Many2one('account.journal', string='Purchase Journal', readonly=True, store=True,
                                          domain=lambda self: [('id', 'in', self.getpurchasejournal())], required=True)
    sales_journal_id = fields.Many2one('account.journal', string='Sales Journal', readonly=True, store=True,
                                       domain = lambda self: [('id', 'in', self.getsalesjournal())], required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)
    cross_line_ids = fields.One2many('mis.crossinvoice.line', 'cross_invoice_id', string='Cross Invlice Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    totalline = fields.Integer('Total Line')
    invoice_id = fields.Many2one('account.move', 'Cross Invoice')


    def button_invoice(self):
        totalamt = 0.00
        move_line_vals = []
        for rec in self.cross_line_ids:
            tax_ids = []
            taxes = rec.tax_ids.filtered(lambda r: not self.company_id or r.company_id == self.company_id)
            tax_ids = taxes.ids
            create_vals = (0, 0, {
                'date': self.trans_date,
                'name': rec.product_id.name,
                'ref': 'Cross Invoice - ' + self.name,
                'tax_ids': tax_ids,
                'parent_state': 'draft',
                'company_id': self.company_id.id,
                'analytic_account_id': rec.analytic_account_id.id,
                'account_id': rec.account_id.id,
                'quantity': rec.quantity,
                'price_unit': rec.price_unit,
                'product_id': rec.product_id.id,
                'analytic_tag_ids': rec.analytic_tag_ids.ids,
            })
            totalamt+=rec.price_total
            move_line_vals.append(create_vals)

        move_vals = {'date': self.trans_date,
                     'partner_id': self.partner_id.id,
                     'invoice_origin': self.name,
                     'invoice_date':  self.trans_date,
                     'journal_id': self.sales_journal_id.id,
                     'ref': 'Cross Invoice - ' + self.name,
                     'name': '/',
                     'company_id': self.company_id.id,
                     'state': 'draft',
                     'type': 'out_invoice',
                     'invoice_line_ids': move_line_vals,
                     }
        objacmove = self.env['account.move'].create(move_vals)
        self.invoice_id = objacmove.id
        self.state = 'posted'
        list_of_ids = []
        list_of_ids.append(objacmove.id)
        if list_of_ids:
            imd = self.env['ir.model.data']
            action = imd.xmlid_to_object('account.action_move_out_invoice_type')
            list_view_id = imd.xmlid_to_res_id('account.view_invoice_tree')
            form_view_id = imd.xmlid_to_res_id('account.view_move_form')
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,
            }
            if list_of_ids:
                result['domain'] = "[('id','in',%s)]" % list_of_ids
        else:
            raise UserError(_('Invoice not generated'))
        return result

    def button_cancel(self):
        self.state='cancel'
    def button_draft(self):
        self.state = 'draft'
    def unlink(self):
        for crossinv in self:
            if crossinv.state != 'draft' and not self._context.get('force_delete'):
                raise UserError(_("You cannot delete an entry which has been posted or cancelled."))
            crossinv.cross_line_ids.unlink()
        return super(MisAuhCrossInvoice, self).unlink()

class MisAuhCrossInvoiceLine(models.Model):
    _name = 'mis.crossinvoice.line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Cross Invoice to Sister Companies Line'

    cross_invoice_id = fields.Many2one('mis.crossinvoice', string='Header ID' , index=True, required=True,
                               ondelete='cascade')
    move_line_id = fields.Many2one('account.move.line', string='Account Move Line')
    product_id = fields.Many2one('product.product', related='move_line_id.product_id', string='Product')
    name = fields.Char(related='move_line_id.name', string='Label')
    account_id = fields.Many2one('account.account', string='Account',
                                 index=True, ondelete="cascade",
                                 domain=[('deprecated', '=', False)])
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    quantity = fields.Float(string='Quantity', related='move_line_id.quantity',
                            default=1.0, digits='Product Unit of Measure',
                            help="The optional quantity expressed by this line, eg: number of product sold. "
                                 "The quantity is not a legal requirement but is very useful for some reports.")
    price_unit = fields.Float(string='Unit Price', related='move_line_id.price_unit', digits='Product Price')
    tax_ids = fields.Many2many('account.tax', string='Taxes')
#    tax_amount = fields.Monetary(string='Tax Amount', related='move_line_id.tax_amount')

    sub_total = fields.Float(string='Sub Total')
    tax_amount = fields.Float(string='Tax Amount')
    price_total = fields.Float(string='Total')

#You have to choose a check layout. For this, go in Apps, search for 'Checks layout' and install one.