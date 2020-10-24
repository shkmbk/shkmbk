from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError


class FFBudgetVariationReport(models.AbstractModel):
    _name = "report.mis_investment.report_budget_variation_document"
    _description = "Fund Flow Budget Variation Report"

    def _get_report_values(self, docids, data=None):
        from_date = data['date_from']
        to_date = data['date_to']
        year = int(data['year'])
        month = int(data['month'])
        year_from = date(year, month, 1)
        year_to = date(year, month, 31)
        obj_budget = self.env['mbk.budget'].search(
            [('state', '=', ['verify', 'done']), ('date_to', '>=', year_from), ('date_to', '<=', year_to)],
            order='date_to, id')
        if not obj_budget:
            raise UserError('No records found in selected parameter')

        master_table = []
        in_flow_table = []
        out_flow_table = []

        # Opening Balance

        for rec in obj_budget:
            year = rec.date_to.year
            month_id = rec.date_to.month
            month = rec.date_to.strftime("%B")
            balance_start = rec.balance_start
            available_fund = 0.00
            fund_budget_expense = 0.00
            fund_actual_expense = 0.00

            particulars_0 = 'Opening Balance'
            particulars_1 = 'Available Fund'
            particulars_2 = 'Fund Requirement'
            particulars_3 = 'Net Fund Position'
            particulars_4 = 'Required Funds'
            particulars_5 = 'Closing Balance'
            particulars_6 = 'Fund Available for Projects'

            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_0)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_0,
                    'budget': balance_start,
                    'actual': rec.balance_start_real,
                    'variation': rec.balance_start_real - balance_start,
                }
                master_table.append(main_line)
            else:
                main_line['budget'] += balance_start
                main_line['actual'] += rec.balance_start_real
                main_line['variation'] += rec.balance_start_real - balance_start

            for in_flow in rec.in_line_ids:
                particulars = in_flow.mbk_project_id.name

                existing_lines = (
                    line_id for line_id in in_flow_table if
                    line_id['particulars'] == particulars)
                main_line = next(existing_lines, False)

                if not main_line:
                    main_line = {
                        'particulars': particulars,
                        'budget': in_flow.budget_amount,
                        'actual': in_flow.actual_amount,
                        'variation': in_flow.actual_amount-in_flow.budget_amount,
                    }
                    in_flow_table.append(main_line)
                else:
                    main_line['budget'] += in_flow.budget_amount
                    main_line['actual'] += in_flow.actual_amount
                    main_line['variation'] += in_flow.actual_amount-in_flow.budget_amount

            # Available Fund

            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_1)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_1,
                    'budget': rec.inflow_budget,
                    'actual': rec.inflow_actual,
                    'variation': rec.inflow_actual - rec.inflow_budget,
                }
                master_table.append(main_line)
            else:
                main_line['budget'] += rec.inflow_budget
                main_line['actual'] += rec.inflow_actual
                main_line['variation'] += rec.inflow_actual - rec.inflow_budget

            for out_flow in rec.out_line_ids:

                if out_flow.mbk_project_id.is_project:
                    particulars = out_flow.mbk_project_id.name

                    existing_lines = (
                        line_id for line_id in out_flow_table if
                        line_id['particulars'] == particulars)
                    main_line = next(existing_lines, False)

                    if not main_line:
                        main_line = {
                            'particulars': particulars,
                            'budget': out_flow.budget_amount,
                            'actual': out_flow.actual_amount,
                            'variation': out_flow.actual_amount - out_flow.budget_amount,
                        }
                        out_flow_table.append(main_line)
                    else:
                        main_line['budget'] += rec.outflow_budget
                        main_line['actual'] += rec.outflow_actual
                        main_line['variation'] += rec.outflow_actual - rec.outflow_budget
                else:
                    fund_budget_expense += out_flow.budget_amount
                    fund_actual_expense += out_flow.actual_amount

            # Fund allocated to Project
            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_6)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_6,
                    'budget': rec.inflow_budget - fund_budget_expense,
                    'actual': rec.inflow_actual - fund_actual_expense,
                    'variation': (rec.inflow_actual - fund_actual_expense)-(rec.inflow_budget - fund_budget_expense),
                }
                master_table.append(main_line)
            else:
                main_line['budget'] += rec.inflow_budget - fund_budget_expense,
                main_line['actual'] += rec.inflow_actual - fund_actual_expense,
                main_line['variation'] += (rec.inflow_actual - fund_actual_expense)-(rec.inflow_budget - fund_budget_expense)

            # Total Fund Requirement
            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_2)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_2,
                    'budget': rec.outflow_budget - fund_budget_expense,
                    'actual': rec.outflow_actual - fund_actual_expense,
                    'variation': (rec.outflow_actual - fund_actual_expense) - (rec.outflow_budget - fund_budget_expense)
                }
                master_table.append(main_line)
            else:
                main_line['budget'] += rec.outflow_budget - fund_budget_expense,
                main_line['actual'] += rec.outflow_actual - fund_actual_expense,
                main_line['variation'] += (rec.outflow_actual - fund_actual_expense) - (rec.outflow_budget - fund_budget_expense)

        # Net Fund Position
            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_3)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_3,
                    'budget': rec.net_fund_position,
                    'actual': rec.net_fund_actual,
                    'variation': rec.net_fund_actual - rec.net_fund_position,
                }
                master_table.append(main_line)
            else:
                main_line['budget'] += rec.net_fund_position,
                main_line['actual'] += rec.net_fund_actual,
                main_line['variation'] += rec.net_fund_actual - rec.net_fund_position

            # Required Funds
            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_4)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_4,
                    'budget': rec.required_fund_budget,
                    'actual': rec.required_fund_actual,
                    'variation': rec.required_fund_actual - rec.required_fund_budget,
                }
                master_table.append(main_line)
            else:
                main_line['budget'] += rec.required_fund_budget,
                main_line['actual'] += rec.required_fund_actual,
                main_line['variation'] += rec.required_fund_actual - rec.required_fund_budget

            # Closing Balance
            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_5)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_5,
                    'budget': rec.balance_end,
                    'actual': rec.balance_end_real,
                    'variation': rec.balance_end_real - rec.balance_end,
                }
                master_table.append(main_line)
            else:
                main_line['budget'] += rec.balance_end,
                main_line['actual'] += rec.balance_end_real,
                main_line['variation'] += rec.balance_end_real - rec.balance_end

        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'mbk.budget',
            'docs': master_table,
            'in_flow_table': in_flow_table,
            'out_flow_table': out_flow_table,
            'year': year,
            'header_period': data['header_period'],
        }
        return docargs
