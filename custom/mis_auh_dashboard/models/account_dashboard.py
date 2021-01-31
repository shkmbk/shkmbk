# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

from odoo import models, api
from odoo.http import request


class AccountsDashBoard(models.Model):
    _inherit = 'account.move'

    # function to Header P&L values
    @api.model
    def get_accounts_profit(self, month_id):

        company_ids = self.get_current_multi_company_value()
        date_id = month_id + '-' + '01'
        month_first_day = datetime.strptime(date_id, '%Y-%m-%d').date()
        month_last_day = month_first_day + relativedelta(months=+1, day=1, days=-1)
        year_first_day = month_first_day.replace(month=1, day=1)
        profit = 0.00
        income = 0.00
        expense = 0.00
        count = 0.00
        this_month_profit = 0.00
        this_month_income = 0.00
        this_month_expense = 0.00
        this_month_count = 0.00
        amount = []
        journal_items = self.env['account.move.line'].search(
            [('parent_state', '=', 'posted'), ('company_id', '=', company_ids),
             ('account_id.internal_group', 'in', ['expense', 'income']), ('date', '>=', year_first_day), ('date', '<=', month_last_day)])
        # raise UserError(company_ids)
        for rec in journal_items:
            profit += rec.credit - rec.debit
            count += 1
            if rec.account_id.internal_group == 'income':
                income += rec.credit - rec.debit
            if rec.account_id.internal_group == 'expense':
                expense += rec.debit - rec.credit

            if month_first_day <= rec.date <= month_last_day:
                this_month_profit += rec.credit - rec.debit
                this_month_count += 1
                if rec.account_id.internal_group == 'income':
                    this_month_income += rec.credit - rec.debit
                if rec.account_id.internal_group == 'expense':
                    this_month_expense += rec.debit - rec.credit

        amount.append({
            'profit': profit,
            'income': income,
            'expense': expense,
            'count': count,
        })
        amount.append({
            'profit': this_month_profit,
            'income': this_month_income,
            'expense': this_month_expense,
            'count': this_month_count,
        })
        return amount

    # Function to get bank & Cash balance
    @api.model
    def get_bank_balance(self):
        company_ids = self.get_current_multi_company_value()
        total_amount = 0.00
        bank = []
        journal_items = self.env['account.move.line'].search(
            [('parent_state', '=', 'posted'), ('company_id', '=', company_ids), ('account_id.user_type_id', '=', 3)])
        # raise UserError(company_ids)
        for rec in journal_items:
            total_amount += rec.debit - rec.credit
            existing_lines = (
                line_id for line_id in bank if
                line_id['particulars'] == rec.account_id.name)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': rec.account_id.name,
                    'amount': rec.debit - rec.credit,
                    'percentage': 0.00,
                }
                bank.append(main_line)
            else:
                main_line['amount'] += rec.debit - rec.credit

        bank_accounts = self.env['account.account'].search(
            [('deprecated', '=', False), ('company_id', '=', company_ids), ('user_type_id', '=', 3),
             ('group_id', '!=', 95)])

        for rec in bank_accounts:
            existing_lines = (
                line_id for line_id in bank if
                line_id['particulars'] == rec.name)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': rec.name,
                    'amount': 0,
                    'percentage': 0.00,
                }
                bank.append(main_line)

        for line in bank:
            line['amount'] = round(line['amount'], 2)
            line['percentage'] = line['particulars'] + ' (' + str(
                round(line['amount'] * 100 / total_amount if total_amount != 0 else 1, 2)) + '%)'

        bank.sort(key=lambda item: (item["amount"]), reverse=True)
        return bank

    # function to get Fixed Deposit Summary
    @api.model
    def get_fixed_deposit(self):
        company_ids = self.get_current_multi_company_value()
        amount = []

        obj_fd = self.env['product.product'].search(
            [('investment_ok', '=', True), ('isdeposit', '=', True), ('maturity_date', '>', date.today()),
             ('categ_id', '=', 15), '|', ('company_id', '=', company_ids), ('company_id', '=', False)])
        # raise UserError(company_ids)
        total_amount = 0.00
        interest_amount = 0.00

        for fd in obj_fd:

            total_amount += fd.list_price
            interest_amount += (fd.expected_earning * ((date.today() - fd.deposit_date).days + 1)) / (
                    fd.maturity_date - fd.deposit_date).days

            existing_lines = (
                line_id for line_id in amount if
                line_id['particulars'] == fd.bank_journal.name)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': fd.bank_journal.name,
                    'amount': fd.list_price,
                    'percentage': 0.00,
                    'type': 0,
                }
                amount.append(main_line)
            else:
                main_line['amount'] += fd.list_price

        for line in amount:
            line['amount'] = round(line['amount'], 2)
            line['percentage'] = line['particulars'] + ' (' + str(
                round(line['amount'] * 100 / total_amount if total_amount != 0 else 1, 2)) + '%)'

        amount.sort(key=lambda item: (item["amount"]), reverse=True)

        if interest_amount > 0:
            amount.append({
                'particulars': 'Interest As On ' + datetime.today().strftime('%d-%m-%Y'),
                'amount': interest_amount,
                'percentage': 'Interest As On ' + datetime.today().strftime('%d-%m-%Y'),
                'type': 1,
            })
        return amount

    # Function to get salary details
    @api.model
    def get_salary_list(self, month_id):
        company_ids = self.get_current_multi_company_value()
        date_id = month_id+'-'+'01'
        month_first_day = datetime.strptime(date_id, '%Y-%m-%d').date()
        month_last_day = month_first_day + relativedelta(months=+1, day=1, days=-1)
        year_first_day = month_first_day.replace(month=1, day=1)
        total_amount = 0.00
        salary = []
        journal_items = self.env['account.move.line'].search(
            [('parent_state', '=', 'posted'), ('company_id', '=', company_ids), ('account_id.group_id', '=', 116), ('date', '>=', year_first_day), ('date', '<=', month_last_day)])
        # raise UserError(company_ids)
        for rec in journal_items:
            total_amount += rec.credit - rec.debit
            existing_lines = (
                line_id for line_id in salary if
                line_id['particulars'] == rec.partner_id.name)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': rec.partner_id.name,
                    'amount': rec.credit - rec.debit,
                }
                salary.append(main_line)
            else:
                main_line['amount'] += rec.credit - rec.debit

        # for line in salary:
        #     line['percentage'] = line['particulars'] + ' (' + str(
        #         round(line['amount'] * 100 / total_amount if total_amount != 0 else 1, 2)) + '%)'

        salary.sort(key=lambda item: (item["amount"]), reverse=True)
        return salary

    # function to P&L chart
    @api.model
    def get_income_expense(self, *post):
        company_ids = self.get_current_multi_company_value()
        date_id = post[1]+'-'+'01'
        month_first_day = datetime.strptime(date_id, '%Y-%m-%d').date()
        month_last_day = month_first_day + relativedelta(months=+1, day=1, days=-1)
        year_first_day = month_first_day.replace(month=1, day=1)

        records = []
        if post[0] == ('income_this_year'):
            journal_items = self.env['account.move.line'].search(
                [('parent_state', '=', 'posted'), ('company_id', '=', company_ids),
                 ('account_id.internal_group', 'in', ['expense', 'income']), ('date', '>=', year_first_day), ('date', '<=', month_last_day)], order='date')
            for rec in journal_items:
                existing_lines = (
                    line_id for line_id in records if
                    line_id['month'] == rec.date.strftime("%b"))
                main_line = next(existing_lines, False)
                if not main_line:
                    main_line = {
                        'month': rec.date.strftime("%b"),
                        'income': (rec.credit - rec.debit) if rec.account_id.internal_group == 'income' else 0.00,
                        'expense': (rec.debit - rec.credit) if rec.account_id.internal_group == 'expense' else 0.00,
                        'profit': rec.credit - rec.debit,
                    }
                    records.append(main_line)
                else:
                    main_line['income'] += (rec.credit - rec.debit) if rec.account_id.internal_group == 'income' else 0.00
                    main_line['expense'] += (rec.debit - rec.credit) if rec.account_id.internal_group == 'expense' else 0.00
                    main_line['profit'] += rec.credit - rec.debit

        else:
            journal_items = self.env['account.move.line'].search(
                [('parent_state', '=', 'posted'), ('company_id', '=', company_ids),
                 ('account_id.internal_group', 'in', ['expense', 'income']), ('date', '>=', month_first_day),
                 ('date', '<=', month_last_day)], order='date')
            for rec in journal_items:
                existing_lines = (
                    line_id for line_id in records if
                    line_id['month'] == rec.date.strftime("%d"))
                main_line = next(existing_lines, False)
                if not main_line:
                    main_line = {
                        'month': rec.date.strftime("%d"),
                        'income': (rec.credit - rec.debit) if rec.account_id.internal_group == 'income' else 0.00,
                        'expense': (rec.debit - rec.credit) if rec.account_id.internal_group == 'expense' else 0.00,
                        'profit': rec.credit - rec.debit,
                    }
                    records.append(main_line)
                else:
                    main_line['income'] += (rec.credit - rec.debit) if rec.account_id.internal_group == 'income' else 0.00
                    main_line['expense'] += (rec.debit - rec.credit) if rec.account_id.internal_group == 'expense' else 0.00
                    main_line['profit'] += rec.credit - rec.debit
        income = []
        expense = []
        month = []
        profit = []
        for rec in records:
            month.append(rec['month'])
            income.append(round(rec['income'], 2))
            expense.append(round(rec['expense'], 2))
            profit.append(round(rec['profit'], 2))
        return {
            'month': month,
            'income': income,
            'expense': expense,
            'profit': profit
        }
        return records


    # Function to get investment summary
    @api.model
    def get_investment_summary_pie(self):
        company_ids = self.get_current_multi_company_value()
        total_amount = 0.00
        investment = []
        journal_items = self.env['account.move.line'].search(
            [('analytic_tag_ids.analytic_tag_group', '=', 35), ('parent_state', '=', 'posted'), ('company_id', '=', company_ids),
             ('account_id.group_id', 'in', [48, 61]), ('account_id', '!=', 2498)])
        # raise UserError(company_ids)
        for rec in journal_items:
            if rec.account_id.account_remark:
                name = rec.account_id.account_remark
            else:
                name = rec.account_id.name

            total_amount += rec.debit - rec.credit
            existing_lines = (
                line_id for line_id in investment if
                line_id['particulars'] == name)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': name,
                    'amount': rec.debit - rec.credit,
                    'percentage': 0.00,
                }
                investment.append(main_line)
            else:
                main_line['amount'] += rec.debit - rec.credit
        label = []
        amount = []
        investment.sort(key=lambda item: (item["amount"]), reverse=True)

        for line in investment:
            line['percentage'] = line['particulars'] + ' (' + str(round(line['amount'] * 100 / total_amount if total_amount != 0 else 1, 2)) + '%)'
            label.append(line['percentage'])
            amount.append(round(line['amount'], 2))

        return {
            'label': label,
            'amount': amount,
            'total_amount': total_amount,
        }
        return records
