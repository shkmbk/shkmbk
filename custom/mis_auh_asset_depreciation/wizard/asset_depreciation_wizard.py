# -*- coding: utf-8 -*-

from odoo import api, fields, models ,_


class AuhAssetDepreciationWizard(models.TransientModel):
    _name = 'asset.depreciation.wizard.custom'
    _description = 'Asset Depreciation Wizard'
    
    is_post = fields.Boolean(string="Is Post", default=False)
    

    def custom_compute_depreciation(self):
        active_ids = self._context.get('active_ids', [])
        depreciation_ids = self.env['account.asset'].search([('id','in',self.env.context['active_ids']),('state','=','draft')])
        for dep in depreciation_ids:
            dep.compute_depreciation_board()
            if self.is_post==True:
                dep.validate()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:   
