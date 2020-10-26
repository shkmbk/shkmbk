# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.tools.misc import formatLang
from dateutil.relativedelta import relativedelta

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset'

    def _sumassetexpense(self):
        objJournal = self.env['account.move.line'].search([('analytic_tag_ids', 'in', self.analytic_tag_ids.ids),
                                                           ('account_id', '!=', self.account_depreciation_expense_id.id),('account_id.internal_group','=','expense')
                                                           ])
        sum=0.00
        for jor in objJournal:
            sum+=jor.balance
        self.sum_asset_expense= sum


    custom_checkbox = fields.Boolean(
        string="Asset Analytic Tag",
        default=False
    )

    sum_asset_expense = fields.Float(string="Total Expenses", compute='_sumassetexpense')
    asset_code = fields.Char(string="Asset Code", track_visibility='onchange')
    asset_group = fields.Many2one('mis.asset.group', string='Group')
    asset_subgroup = fields.Many2one('mis.asset.subgroup', string='Sub Group')
    asset_brand = fields.Many2one('mis.asset.brand', string='Asset Brand')
    asset_location = fields.Many2one('mis.asset.location', string='Location')
    asset_sublocation = fields.Many2one('mis.asset.sublocation', string='Sub Location', domain="[('main_location', '=', asset_location)]")
    asset_custodian = fields.Many2one('mis.asset.custodian', string='Custodian')
    asset_purchase_date = fields.Date(string="Purchase Date")
    asset_purchase_amount = fields.Monetary(string="Purchase Amount")
    asset_area = fields.Many2one('mis.asset.area', string='Area')
    is_opening = fields.Boolean(string="Opening Asset",default=False)
    asset_qty = fields.Float(string="Quantity", default=1)
    asset_cost = fields.Float(string="Cost")
    asset_description = fields.Char(string="Asset Description")
    op_duration = fields.Integer(string="Asset Duration")

    _sql_constraints = [
            ('code_uniq', 'unique (asset_code)', "Asset Code already exists !"),
        ]

    @api.model
    def create(self, vals):
        asset = super(AccountAssetAsset, self).create(vals)
        if vals.get('custom_checkbox')==True:
            group_id=0
            group_tag = self.env['mis.analytic.tag.group'].search([('name', '=', 'Fixed Asset')])
            if group_tag:
                for gr in group_tag:
                    group_id=gr.id
            else:
                group_tag = self.env['mis.analytic.tag.group'].create({'name':'Fixed Asset'})
                group_id = group_tag.id

            code =  vals['name'] + '(' + vals['asset_code'] + ')'
            
            obj_tag_id = self.env['account.analytic.tag'].search([('name', '=', code), ('company_id', '=', self.env.company.id)], limit=1)
            if obj_tag_id:
                tag_ids = obj_tag_id
            else: 
                tag_ids = self.env['account.analytic.tag'].create({
                    'name':code, 'analytic_tag_group': group_id,
                    'company_id': self.env.company.id,
                    })
            asset.analytic_tag_ids = tag_ids.ids + asset.analytic_tag_ids.ids
        return asset

    def write(self, vals):
        asset = super(AccountAssetAsset, self).write(vals)
        if vals.get('custom_checkbox') == True and not self.analytic_tag_ids:
            group_id = 0
            group_tag = self.env['mis.analytic.tag.group'].search([('name', '=', 'Fixed Asset')])
            if group_tag:
                for gr in group_tag:
                    group_id = gr.id
            else:
                group_tag = self.env['mis.analytic.tag.group'].create({'name': 'Fixed Asset'})
                group_id = group_tag.id

            code = self.name + '(' + self.asset_code + ')'
            obj_tag_id = self.env['account.analytic.tag'].search([('name', '=', code), ('company_id', '=', self.env.company.id)], limit=1)
            if obj_tag_id:
                tag_ids = obj_tag_id
            else: 
                tag_ids = self.env['account.analytic.tag'].create({
                    'name':code, 'analytic_tag_group': group_id,
                    'company_id': self.env.company.id,
                    })

            self.analytic_tag_ids = tag_ids.ids + self.analytic_tag_ids.ids
        return asset

    def action_custom_exapense_show(self):
        journal_entry = []
        journal_items = self.env['account.move.line'].search([('analytic_tag_ids','in',self.analytic_tag_ids.ids),('account_id.internal_group','=','expense'), ('account_id', '!=', self.account_depreciation_expense_id.id)])
        for j in journal_items:
            journal_entry.append(j.move_id.id)
        return {
            'name': _('Journal Entries'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', journal_entry)],
        }

    @api.onchange('journal_id')
    def _onchange_journal(self):
        for frm in self:
            if frm.journal_id.analytic_id:
                frm.account_analytic_id = frm.journal_id.analytic_id.id

    @api.onchange('asset_group', 'asset_subgroup')
    def _onchange_accountcode(self):
        if self.state !='model':
            if self.asset_group:
                if self.asset_subgroup:
                    companyid = self.company_id.id
                    isFound=False
                    if self.asset_code:
                        objisfound = self.env['account.asset'].search([('asset_code', '=', self.asset_code), ('company_id', '=', companyid)])
                        if objisfound:
                            isFound=True
                    if  isFound==False:
                        cle_query = "select right(max(asset_code), 5) as maxcode  from account_asset where company_id=" + str(companyid) +" and not asset_code is null and asset_group = " + str(self.asset_group.id) +  " and asset_subgroup = " + str(self.asset_subgroup.id)
                        self.env.cr.execute(cle_query)
                        cle_data = self.env.cr.dictfetchall()
                        strcode=''
                        for row in cle_data:
                            strcode= row['maxcode']
                        #last_id = self.env['account.asset'].search([('asset_group', '=', self.asset_group.id), ('asset_subgroup', '=', self.asset_subgroup.id), ('asset_code', '!=', '')], order='asset_code desc')[0].asset_code
                        if strcode:
                            strcode = "00000" + str(int(strcode) + 1)
                            self.asset_code= str(self.asset_group.code)+ str(self.asset_subgroup.code)+ "-" + strcode[-5:]
                        else:
                            self.asset_code =str(self.asset_group.code)+ str(self.asset_subgroup.code)+"-00001"


class MisAuhAssetGroup(models.Model):
    _name = 'mis.asset.group'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    code = fields.Char(string="Code", required=True, track_visibility='onchange')
    name = fields.Char(string="Group",  required=True, track_visibility='onchange')

    _sql_constraints = [
            ('name_uniq', 'unique (Code)', "Asset Group Code already exists !"),
    ]
class MisAuhAssetSubGroup(models.Model):
    _name = 'mis.asset.subgroup'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    code = fields.Char(string="Code", required=True, track_visibility='onchange')
    name = fields.Char(string="Sub Group",  required=True, track_visibility='onchange')

    _sql_constraints = [
            ('name_uniq', 'unique (code)', "Asset Sub Group code already exists !"),
    ]
class MisAuhAssetLocation(models.Model):
    _name = 'mis.asset.location'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Location",  required=True, track_visibility='onchange')

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Asset Location already exists !"),
    ]

class MisAuhAssetSubLocation(models.Model):
    _name = 'mis.asset.sublocation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    main_location = fields.Many2one('mis.asset.location', string="Main Location", required="1")
    name = fields.Char(string="Sub Location",  required=True, track_visibility='onchange')


    _sql_constraints = [
            ('name_uniq', 'unique (main_location, name)', "Asset Sub Location already exists in the same main location !"),
    ]

class MisAuhAssetBrand(models.Model):
    _name = 'mis.asset.brand'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Asset Brand",  required=True, track_visibility='onchange')

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Asset Brand already exists !"),
    ]

class MisAuhAssetCustodian(models.Model):
    _name = 'mis.asset.custodian'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Custodian",  required=True, track_visibility='onchange')

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Asset Custodian already exists !"),
    ]
class MisAuhAssetArea(models.Model):
    _name = 'mis.asset.area'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Asset Area",  required=True, track_visibility='onchange')

    _sql_constraints = [
            ('name_uniq', 'unique (name)', "Asset Area already exists !"),
    ]

class AssetAccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _prepare_move_for_asset_depreciation(self, vals):
        missing_fields = set(['asset_id', 'move_ref', 'amount', 'asset_remaining_value', 'asset_depreciated_value']) - set(vals)
        if missing_fields:
            raise UserError(_('Some fields are missing {}').format(', '.join(missing_fields)))
        asset = vals['asset_id']
        account_analytic_id = asset.account_analytic_id
        analytic_tag_ids = asset.analytic_tag_ids
        depreciation_date = vals.get('date', fields.Date.context_today(self))
        company_currency = asset.company_id.currency_id
        current_currency = asset.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(vals['amount'], company_currency, asset.company_id, depreciation_date)
        move_line_1 = {
            'name': asset.name,
            'account_id': asset.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'analytic_account_id': account_analytic_id.id if asset.asset_type in ('purchase', 'sale', 'expense')  else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if asset.asset_type  in ('purchase', 'sale', 'expense')  else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * vals['amount'] or 0.0,
        }
        move_line_2 = {
            'name': asset.name,
            'account_id': asset.account_depreciation_expense_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'analytic_account_id': account_analytic_id.id if asset.asset_type in ('purchase', 'sale', 'expense') else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if asset.asset_type in ('purchase', 'sale', 'expense') else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and vals['amount'] or 0.0,
        }
        move_vals = {
            'ref': vals['move_ref'],
            'date': depreciation_date,
            'journal_id': asset.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            'auto_post': asset.state == 'open',
            'asset_id': asset.id,
            'asset_remaining_value': vals['asset_remaining_value'],
            'asset_depreciated_value': vals['asset_depreciated_value'],
            'amount_total': amount,
            'name': '/',
            'asset_value_change': vals.get('asset_value_change', False),
            'type': 'entry',
            'currency_id': current_currency.id,
        }
        return move_vals

