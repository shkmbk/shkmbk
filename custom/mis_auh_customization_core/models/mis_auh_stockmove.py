from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero
import logging
_logger = logging.getLogger(__name__)

class MisAuhStockPicking(models.Model):
    _inherit = "stock.picking"

    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    @api.onchange('analytic_id')
    def _onchange_analytic(self):
        for line in self.move_ids_without_package:
            line.analytic_account_id = self.analytic_id.id
            line.parent_analytic_id = self.analytic_id.id

class MisStockMoveLine(models.Model):
    _inherit = "stock.move.line"

    parent_analytic_id = fields.Many2one('account.analytic.account', related='picking_id.analytic_id')

class MisStockMove(models.Model):
    _inherit = "stock.move"

    @api.onchange('product_id')
    def _onchange_analytic(self):
        for line in self:
            line.analytic_account_id = self.picking_id.analytic_id.id
            line.parent_analytic_id = self.picking_id.analytic_id.id


    parent_analytic_id = fields.Many2one('account.analytic.account', related='picking_id.analytic_id')

class MisAuhPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order'

    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', store=True)

#     @api.model
#     def _prepare_picking(self):
#
#         if not self.group_id:
#             self.group_id = self.group_id.create({
#                 'name': self.name,
#                 'partner_id': self.partner_id.id
#             })
#         if not self.partner_id.property_stock_supplier.id:
#             raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
#         return {
#             'picking_type_id': self.picking_type_id.id,
#             'partner_id': self.partner_id.id,
#             'user_id': False,
#             'date': self.date_order,
#             'origin': self.name,
#             'analytic_id': self.journal_id.analytic_id.id,
#             'location_dest_id': self._get_destination_location(),
#             'location_id': self.partner_id.property_stock_supplier.id,
#             'company_id': self.company_id.id,
#         }
#
# class Mis_Auh_StockMove(models.Model):
#     _inherit = 'stock.move'
#     def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
#         """ Overridden from stock_account to support amount_currency on valuation lines generated from po
#         """
#         self.ensure_one()
#
#         rslt = super(Mis_Auh_StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description)
#         if self.purchase_line_id:
#             purchase_currency = self.purchase_line_id.currency_id
#             if purchase_currency != self.company_id.currency_id:
#                 # Do not use price_unit since we want the price tax excluded. And by the way, qty
#                 # is in the UOM of the product, not the UOM of the PO line.
#                 purchase_price_unit = (
#                     self.purchase_line_id.price_subtotal / self.purchase_line_id.product_uom_qty
#                     if self.purchase_line_id.product_uom_qty
#                     else self.purchase_line_id.price_unit
#                 )
#                 currency_move_valuation = purchase_currency.round(purchase_price_unit * abs(qty))
#                 rslt['credit_line_vals']['amount_currency'] = rslt['credit_line_vals']['credit'] and -currency_move_valuation or currency_move_valuation
#                 rslt['credit_line_vals']['currency_id'] = purchase_currency.id
#                 rslt['debit_line_vals']['amount_currency'] = rslt['debit_line_vals']['credit'] and -currency_move_valuation or currency_move_valuation
#                 rslt['debit_line_vals']['currency_id'] = purchase_currency.id
#             if  self.purchase_line_id.order_id.journal_id.analytic_id:
#                 rslt['credit_line_vals']['analytic_account_id'] = self.purchase_line_id.order_id.journal_id.analytic_id.id,
#                 rslt['debit_line_vals']['analytic_account_id'] = self.purchase_line_id.order_id.journal_id.analytic_id.id,
#
#         if self.sale_line_id:
#             if self.sale_line_id.order_id.journal_id.analytic_id:
#                 rslt['credit_line_vals']['analytic_account_id'] = self.sale_line_id.order_id.journal_id.analytic_id.id,
#                 rslt['debit_line_vals']['analytic_account_id'] = self.sale_line_id.order_id.journal_id.analytic_id.id,
#
# #            raise UserError(str(rslt['credit_line_vals']['analytic_account_id']) +' --> ' + str(self.sale_line_id.order_id.journal_id.analytic_id.id))
#
#
#         return rslt
