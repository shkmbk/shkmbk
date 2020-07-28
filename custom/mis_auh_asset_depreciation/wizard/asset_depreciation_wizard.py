# -*- coding: utf-8 -*-

from odoo import api, fields, models ,_


class AuhAssetDepreciationWizard(models.TransientModel):
    _name = 'asset.depreciation.wizard.custom'
    _description = 'Asset Depreciation Wizard'


    def custom_compute_depreciation(self):
        active_ids = self._context.get('active_ids', [])
        depreciation_ids = self.env['account.asset'].browse(self.env.context['active_ids'])
        for dep in depreciation_ids:
            dep.compute_depreciation_board()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:   
