# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

from odoo import models, api
from odoo.http import request


class InvestmentDashBoard(models.Model):
    _inherit = 'account.move'

    # function to Header P&L values
    @api.model
    def get_investment_profit(self):

        company_ids = self.get_current_multi_company_value()
        month_first_day = date.today().replace(day=1)
        month_last_day = date.today() + relativedelta(months=+1, day=1, days=-1)
        profit = 0.00
        income = 0.00
        expense = 0.00
        this_month_profit = 0.00
        this_month_income = 0.00
        this_month_expense = 0.00
        amount = []
        journal_items = self.env['account.move.line'].search(
            [('analytic_tag_ids.analytic_tag_group', '=', 35), ('parent_state', '=', 'posted'), ('company_id', '=', company_ids),
             ('account_id.internal_group', 'in', ['expense', 'income'])])
        # raise UserError(company_ids)
        for rec in journal_items:
            profit += rec.credit - rec.debit
            if rec.account_id.internal_group == 'income':
                income += rec.credit - rec.debit
            if rec.account_id.internal_group == 'expense':
                expense += rec.debit - rec.credit

            if month_first_day <= rec.date <= month_last_day:
                this_month_profit += rec.credit - rec.debit
                if rec.account_id.internal_group == 'income':
                    this_month_income += rec.credit - rec.debit
                if rec.account_id.internal_group == 'expense':
                    this_month_expense += rec.debit - rec.credit

        amount.append({
            'profit': profit,
            'income': income,
            'expense': expense,
        })
        amount.append({
            'profit': this_month_profit,
            'income': this_month_income,
            'expense': this_month_expense,
        })
        return amount

    # Function to get investment asset values
    @api.model
    def get_investment_values(self):

        company_ids = self.get_current_multi_company_value()
        month_first_day = date.today().replace(day=1)
        month_last_day = date.today() + relativedelta(months=+1, day=1, days=-1)
        this_year_investment = 0.00
        this_month_investment = 0.00
        investment = []
        journal_items = self.env['account.move.line'].search(
            [('analytic_tag_ids.analytic_tag_group', '=', 35), ('parent_state', '=', 'posted'), ('company_id', '=', company_ids),
             ('account_id.group_id', 'in', [48, 61]), ('account_id', '!=', 2498)])
        # raise UserError(company_ids)
        for rec in journal_items:
            this_year_investment += rec.debit - rec.credit
            if month_first_day <= rec.date <= month_last_day:
                this_month_investment += rec.debit - rec.credit

        investment.append({
            'investment': this_year_investment,
        })
        investment.append({
            'investment': this_month_investment,
        })
        return investment

    # Function to get investment summary
    @api.model
    def get_investment_summary(self):
        company_ids = self.get_current_multi_company_value()
        total_amount = 0.00
        investment = []
        journal_items = self.env['account.move.line'].search(
            [('analytic_tag_ids.analytic_tag_group', '=', 35), ('parent_state', '=', 'posted'), ('company_id', '=', company_ids),
             ('account_id.group_id', 'in', [48, 61]), ('account_id', '!=', 2498)])
        # raise UserError(company_ids)
        for rec in journal_items:
            total_amount += rec.debit - rec.credit
            existing_lines = (
                line_id for line_id in investment if
                line_id['particulars'] == rec.account_id.name)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': rec.account_id.name,
                    'amount': rec.debit - rec.credit,
                    'percentage': 0.00,
                }
                investment.append(main_line)
            else:
                main_line['amount'] += rec.debit - rec.credit
        for line in investment:
            line['percentage'] = line['particulars']+' ('+str(round(line['amount']*100/total_amount if total_amount != 0 else 1, 2))+'%)'

        investment.sort(key=lambda item: (item["amount"]), reverse=True)
        return investment

    # Function to get Fixed Asset summary
    @api.model
    def get_fd_summary(self):
        company_ids = self.get_current_multi_company_value()
        total_amount = 0.00
        fd = []
        journal_items = self.env['account.move.line'].search(
            [('analytic_tag_ids.analytic_tag_group', '=', 35), ('parent_state', '=', 'posted'), ('company_id', '=', company_ids),
             ('account_id.code', 'in', ['111801', '111802'])])
        # raise UserError(company_ids)
        for rec in journal_items:
            total_amount += rec.debit - rec.credit
            existing_lines = (
                line_id for line_id in fd if
                line_id['particulars'] == rec.analytic_tag_ids.name)
            main_line = next(existing_lines, False)
            total_amount += rec.debit - rec.credit
            if not main_line:
                main_line = {
                    'particulars': rec.analytic_tag_ids.name,
                    'amount': rec.debit - rec.credit,
                    'percentage': 0.00,
                }
                fd.append(main_line)
            else:
                main_line['amount'] += rec.debit - rec.credit
        for line in fd:
            line['percentage'] = line['particulars']+' ('+str(round(line['amount']*100/total_amount if total_amount != 0 else 1, 2))+'%)'

        fd.sort(key=lambda item: (item["amount"]), reverse=True)
        return fd

    # function to P&L summary values
    @api.model
    def get_investment_pl_summary(self):

        company_ids = self.get_current_multi_company_value()
        share_pl = 0.00
        fd_pl = 0.00
        bond_pl = 0.00

        amount = []
        journal_items = self.env['account.move.line'].search(
            [('analytic_tag_ids.analytic_tag_group', '=', 35), ('parent_state', '=', 'posted'), ('company_id', '=', company_ids),
             ('account_id.internal_group', 'in', ['expense', 'income'])])
        # raise UserError(company_ids)
        for rec in journal_items:
            if rec.account_id.group_id.id == 75:
                share_pl += rec.credit - rec.debit
            if rec.account_id.group_id.id == 122:
                bond_pl += rec.credit - rec.debit
            if rec.account_id.id == 287:
                fd_pl += rec.credit - rec.debit

        total_pl = share_pl + bond_pl + fd_pl

        if share_pl != 0.00:
            amount.append({
                'particulars': 'Inv. in Sec. - Listed Stock',
                'amount': share_pl,
                'percentage': 'Inv. in Sec. - Listed Stock (' + str(round(share_pl*100/total_pl if total_pl != 0 else 1, 2))+'% )',
            })
        if bond_pl != 0:
            amount.append({
                'particulars': 'Inv. in Sec. - Debentures',
                'amount': bond_pl,
                'percentage': 'Inv. in Sec. - Debentures (' + str(round(bond_pl*100/total_pl if total_pl != 0 else 1, 2))+'% )',
            })
        if fd_pl != 0:
            amount.append({
                'particulars': 'Fixed Deposits',
                'amount': fd_pl,
                'percentage': 'Fixed Deposits (' + str(round(fd_pl*100/total_pl if total_pl != 0 else 1, 2))+'% )',
            })
        amount.sort(key=lambda item: (item["amount"]), reverse=True)
        return amount

# function to get Investment Securities values
    @api.model
    def get_securities_summary(self):
        company_ids = self.get_current_multi_company_value()
        total_amount = 0.00
        securities = []
        journal_items = self.env['account.move.line'].search(
            [('analytic_tag_ids.analytic_tag_group', '=', 35), ('parent_state', '=', 'posted'), ('company_id', '=', company_ids),
             ('account_id', 'in', [2309, 2538])])
        # raise UserError(company_ids)
        for rec in journal_items:
            total_amount += rec.debit - rec.credit
            existing_lines = (
                line_id for line_id in securities if
                line_id['particulars'] == rec.analytic_tag_ids.name)
            main_line = next(existing_lines, False)
            total_amount += round(rec.debit - rec.credit, 2)
            if not main_line:
                main_line = {
                    'particulars': rec.analytic_tag_ids.name,
                    'amount': round(rec.debit - rec.credit, 2),
                    'percentage': 0.00,
                }
                securities.append(main_line)
            else:
                main_line['amount'] += rec.debit - rec.credit
        for line in securities:
            line['percentage'] = line['particulars']+' ('+str(round(line['amount']*100/total_amount if total_amount != 0 else 1, 2))+'%)'

        securities.sort(key=lambda item: (item["amount"]), reverse=True)
        return securities

# function to get Share Investment market value change
    @api.model
    def get_share_change(self):
        company_ids = self.get_current_multi_company_value()
        amount = []

        obj_share = self.env['product.product'].search([('investment_ok', '=', True), ('type', '=', 'product'), ('categ_id', '=', 5), '|', ('company_id', '=', company_ids), ('company_id', '=', False)])
        # raise UserError(company_ids)
        total_amount = 0.00
        for share in obj_share:
            obj_stock = self.env['stock.valuation.layer'].search([('product_id', '=', share.id)])
            qty = 0.0
            closing_amount = 0.00
            cost = 0.00
            price_change = 0.00
            value_change = 0.00

            for gr in obj_stock:
                qty += gr.quantity
                closing_amount += gr.value
            if qty != 0.00:
                cost = closing_amount/qty

            objlastvaluation = self.env['mis.invrevaluation.line'].search([('revaluation_id.state', '=', 'posted'), ('share_id', '=', share.id)], order='revaluation_id desc', limit=1)
            if objlastvaluation:
                market_price = objlastvaluation.closingprice
            else:
                market_price = cost
            market_value = qty * market_price

            price_change = market_price - cost
            value_change = market_value - closing_amount
            if closing_amount != 0:
                percentage_change = round(value_change*100/closing_amount, 2)
            else:
                percentage_change = 0

            total_amount += value_change

            if qty != 0.00:
                amount.append({
                    'particulars': share.name,
                    'amount': value_change,
                    'percentage': share.name+' ('+str(percentage_change)+'%)',
                    'pc': percentage_change,
                })

        amount.sort(key=lambda item: (item["pc"]), reverse=True)
        return amount

# function to Share P&L breakup values
    @api.model
    def get_share_pl_summary(self):

        company_ids = self.get_current_multi_company_value()

        amount = []
        journal_items = self.env['account.move.line'].search(
            [('analytic_tag_ids.analytic_tag_group', '=', 35), ('parent_state', '=', 'posted'), ('company_id', '=', company_ids),
             ('account_id.internal_group', 'in', ['expense', 'income']), ('account_id.group_id', '=', 75)])
        # raise UserError(company_ids)
        for rec in journal_items:
            if rec.account_id.account_remark:
                name = rec.account_id.account_remark
            else:
                name = rec.account_id.name

            existing_lines = (
                line_id for line_id in amount if
                line_id['particulars'] == name)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': name,
                    'amount': rec.credit-rec.debit,
                }
                amount.append(main_line)
            else:
                main_line['amount'] += rec.credit-rec.debit

        amount.sort(key=lambda item: (item["amount"]), reverse=True)
        return amount
