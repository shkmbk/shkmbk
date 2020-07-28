# -*- coding: utf-8 -*-

from odoo import fields, models

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for re in res:
            re['analytic_account_id'] = self.account_analytic_id.id
            re['custom_analytic_tag_ids'] = [(6, 0, self.analytic_tag_ids.ids)]
        return res
    

