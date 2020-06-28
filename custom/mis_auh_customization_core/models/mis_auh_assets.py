# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MisAuhAssets(models.Model):
    _inherit = 'account.asset'

    asset_code = fields.Char(string="Asset Code", track_visibility='onchange')
    asset_group = fields.Many2one('mis.asset.group', string='Group')
    asset_subgroup = fields.Many2one('mis.asset.subgroup', string='Sub Group')
    asset_brand = fields.Many2one('mis.asset.brand', string='Asset Brand')
    asset_location = fields.Many2one('mis.asset.location', string='Location')
    asset_custodian = fields.Many2one('mis.asset.custodian', string='Custodian')



    _sql_constraints = [
            ('code_uniq', 'unique (asset_code)', "Asset Code already exists !"),
        ]

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
                    companyid = self.env.user.company_id.id
                    isNotFound=True
                    if self.asset_code:
                        objisfound = self.env['account.asset'].search([('asset_code', '=', self.asset_code)])
                        if objisfound:
                            isNotFound=False

                    if  isNotFound:

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


