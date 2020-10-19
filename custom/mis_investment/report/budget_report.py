from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError


class FFBudgetReport(models.AbstractModel):
    _name = "report.mis_investment.report_budget_document"
    _description = "Fund Flow Budget Report"

    def _get_report_values(self, docids, data=None):
        from_date = data['date_from']
        to_date = data['date_to']
        year = int(data['year'])
        year_from = date(year, 1, 1)
        year_to = date(year, 12, 31)
        obj_budget = self.env['mbk.budget'].search(
            [('state', '=', ['verify', 'done']), ('date_to', '>=', year_from), ('date_to', '<=', year_to)],
            order='date_to')
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
            balance_end_real = rec.balance_end_real
            balance_end = rec.balance_end
            net_fund_position = rec.net_fund_position
            net_fund_actual = rec.net_fund_actual
            net_fund_variance = rec.net_fund_variance
            required_fund_budget = rec.required_fund_budget
            required_fund_actual = rec.required_fund_actual
            required_fund_variance = rec.required_fund_variance
            available_fund = balance_start
            fund_requirement = 0.00
            closing_balance = 0.00
            if rec.state == 'done':
                closing_balance = balance_end_real
            else:
                closing_balance = balance_end

            particulars_0 = 'Opening Balance'
            particulars_1 = 'Available Fund'
            particulars_2 = 'Fund Requirement'
            particulars_3 = 'Net Fund Position'
            particulars_4 = 'Required Funds'
            particulars_5 = 'Closing Balance'

            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_0)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_0,
                    'january': balance_start if month_id == 1 else 0.00,
                    'february': balance_start if month_id == 2 else 0.00,
                    'march': balance_start if month_id == 3 else 0.00,
                    'april': balance_start if month_id == 4 else 0.00,
                    'may': balance_start if month_id == 5 else 0.00,
                    'june': balance_start if month_id == 5 else 0.00,
                    'july': balance_start if month_id == 7 else 0.00,
                    'august': balance_start if month_id == 8 else 0.00,
                    'september': balance_start if month_id == 9 else 0.00,
                    'october': balance_start if month_id == 10 else 0.00,
                    'november': balance_start if month_id == 11 else 0.00,
                    'december': balance_start if month_id == 12 else 0.00,
                }
                master_table.append(main_line)
            else:
                main_line['january'] += balance_start if month_id == 1 else 0.00
                main_line['february'] += balance_start if month_id == 2 else 0.00
                main_line['march'] += balance_start if month_id == 3 else 0.00
                main_line['april'] += balance_start if month_id == 4 else 0.00
                main_line['may'] += balance_start if month_id == 5 else 0.00
                main_line['june'] += balance_start if month_id == 6 else 0.00
                main_line['july'] += balance_start if month_id == 7 else 0.00
                main_line['august'] += balance_start if month_id == 8 else 0.00
                main_line['september'] += balance_start if month_id == 9 else 0.00
                main_line['october'] += balance_start if month_id == 10 else 0.00
                main_line['november'] += balance_start if month_id == 11 else 0.00
                main_line['december'] += balance_start if month_id == 12 else 0.00

            for in_flow in rec.in_line_ids:
                january = 0.00
                february = 0.00
                march = 0.00
                april = 0.00
                may = 0.00
                june = 0.00
                july = 0.00
                august = 0.00
                september = 0.00
                october = 0.00
                november = 0.00
                december = 0.00
                
                particulars = in_flow.mbk_project_id.name                
                available_fund += in_flow.budget_amount
                
                if month_id == 1:
                    january += in_flow.budget_amount
                if month_id == 2:
                    february += in_flow.budget_amount
                if month_id == 3:
                    march += in_flow.budget_amount
                if month_id == 4:
                    april += in_flow.budget_amount
                if month_id == 5:
                    may += in_flow.budget_amount
                if month_id == 6:
                    june += in_flow.budget_amount
                if month_id == 7:
                    july += in_flow.budget_amount
                if month_id == 8:
                    august += in_flow.budget_amount
                if month_id == 9:
                    september += in_flow.budget_amount
                if month_id == 10:
                    october += in_flow.budget_amount
                if month_id == 11:
                    november += in_flow.budget_amount
                if month_id == 12:
                    december += in_flow.budget_amount

                existing_lines = (
                    line_id for line_id in in_flow_table if
                    line_id['particulars'] == particulars)
                main_line = next(existing_lines, False)

                if not main_line:
                    main_line = {
                        'particulars': particulars,
                        'january': january,
                        'february': february,
                        'march': march,
                        'april': april,
                        'may': may,
                        'june': june,
                        'july': july,
                        'august': august,
                        'september': september,
                        'october': october,
                        'november': november,
                        'december': december,
                    }
                    in_flow_table.append(main_line)
                else:
                    main_line['january'] += january
                    main_line['february'] += february
                    main_line['march'] += march
                    main_line['april'] += april
                    main_line['may'] += may
                    main_line['june'] += june
                    main_line['july'] += july
                    main_line['august'] += august
                    main_line['september'] += september
                    main_line['october'] += october
                    main_line['november'] += november
                    main_line['december'] += december
            # Available Fund                    
            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_1)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_1,
                    'january': available_fund if month_id == 1 else 0.00,
                    'february': available_fund if month_id == 2 else 0.00,
                    'march': available_fund if month_id == 3 else 0.00,
                    'april': available_fund if month_id == 4 else 0.00,
                    'may': available_fund if month_id == 5 else 0.00,
                    'june': available_fund if month_id == 5 else 0.00,
                    'july': available_fund if month_id == 7 else 0.00,
                    'august': available_fund if month_id == 8 else 0.00,
                    'september': available_fund if month_id == 9 else 0.00,
                    'october': available_fund if month_id == 10 else 0.00,
                    'november': available_fund if month_id == 11 else 0.00,
                    'december': available_fund if month_id == 12 else 0.00,
                }
                master_table.append(main_line)
            else:
                main_line['january'] += available_fund if month_id == 1 else 0.00
                main_line['february'] += available_fund if month_id == 2 else 0.00
                main_line['march'] += available_fund if month_id == 3 else 0.00
                main_line['april'] += available_fund if month_id == 4 else 0.00
                main_line['may'] += available_fund if month_id == 5 else 0.00
                main_line['june'] += available_fund if month_id == 6 else 0.00
                main_line['july'] += available_fund if month_id == 7 else 0.00
                main_line['august'] += available_fund if month_id == 8 else 0.00
                main_line['september'] += available_fund if month_id == 9 else 0.00
                main_line['october'] += available_fund if month_id == 10 else 0.00
                main_line['november'] += available_fund if month_id == 11 else 0.00
                main_line['december'] += available_fund if month_id == 12 else 0.00

            for out_flow in rec.out_line_ids:
                january = 0.00
                february = 0.00
                march = 0.00
                april = 0.00
                may = 0.00
                june = 0.00
                july = 0.00
                august = 0.00
                september = 0.00
                october = 0.00
                november = 0.00
                december = 0.00
                particulars = out_flow.mbk_project_id.name
                fund_requirement += out_flow.budget_amount

                if month_id == 1:
                    january += out_flow.budget_amount
                if month_id == 2:
                    february += out_flow.budget_amount
                if month_id == 3:
                    march += out_flow.budget_amount
                if month_id == 4:
                    april += out_flow.budget_amount
                if month_id == 5:
                    may += out_flow.budget_amount
                if month_id == 6:
                    june += out_flow.budget_amount
                if month_id == 7:
                    july += out_flow.budget_amount
                if month_id == 8:
                    august += out_flow.budget_amount
                if month_id == 9:
                    september += out_flow.budget_amount
                if month_id == 10:
                    october += out_flow.budget_amount
                if month_id == 11:
                    november += out_flow.budget_amount
                if month_id == 12:
                    december += out_flow.budget_amount

                existing_lines = (
                    line_id for line_id in out_flow_table if
                    line_id['particulars'] == particulars)
                main_line = next(existing_lines, False)

                if not main_line:
                    main_line = {
                        'particulars': particulars,
                        'january': january,
                        'february': february,
                        'march': march,
                        'april': april,
                        'may': may,
                        'june': june,
                        'july': july,
                        'august': august,
                        'september': september,
                        'october': october,
                        'november': november,
                        'december': december,
                    }
                    out_flow_table.append(main_line)
                else:
                    main_line['january'] += january
                    main_line['february'] += february
                    main_line['march'] += march
                    main_line['april'] += april
                    main_line['may'] += may
                    main_line['june'] += june
                    main_line['july'] += july
                    main_line['august'] += august
                    main_line['september'] += september
                    main_line['october'] += october
                    main_line['november'] += november
                    main_line['december'] += december
            # Total Fund Requirement
            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_2)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_2,
                    'january': fund_requirement if month_id == 1 else 0.00,
                    'february': fund_requirement if month_id == 2 else 0.00,
                    'march': fund_requirement if month_id == 3 else 0.00,
                    'april': fund_requirement if month_id == 4 else 0.00,
                    'may': fund_requirement if month_id == 5 else 0.00,
                    'june': fund_requirement if month_id == 5 else 0.00,
                    'july': fund_requirement if month_id == 7 else 0.00,
                    'august': fund_requirement if month_id == 8 else 0.00,
                    'september': fund_requirement if month_id == 9 else 0.00,
                    'october': fund_requirement if month_id == 10 else 0.00,
                    'november': fund_requirement if month_id == 11 else 0.00,
                    'december': fund_requirement if month_id == 12 else 0.00,
                }
                master_table.append(main_line)
            else:
                main_line['january'] += fund_requirement if month_id == 1 else 0.00
                main_line['february'] += fund_requirement if month_id == 2 else 0.00
                main_line['march'] += fund_requirement if month_id == 3 else 0.00
                main_line['april'] += fund_requirement if month_id == 4 else 0.00
                main_line['may'] += fund_requirement if month_id == 5 else 0.00
                main_line['june'] += fund_requirement if month_id == 6 else 0.00
                main_line['july'] += fund_requirement if month_id == 7 else 0.00
                main_line['august'] += fund_requirement if month_id == 8 else 0.00
                main_line['september'] += fund_requirement if month_id == 9 else 0.00
                main_line['october'] += fund_requirement if month_id == 10 else 0.00
                main_line['november'] += fund_requirement if month_id == 11 else 0.00
                main_line['december'] += fund_requirement if month_id == 12 else 0.00

        # Net Fund Position
            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_3)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_3,
                    'january': net_fund_position if month_id == 1 else 0.00,
                    'february': net_fund_position if month_id == 2 else 0.00,
                    'march': net_fund_position if month_id == 3 else 0.00,
                    'april': net_fund_position if month_id == 4 else 0.00,
                    'may': net_fund_position if month_id == 5 else 0.00,
                    'june': net_fund_position if month_id == 5 else 0.00,
                    'july': net_fund_position if month_id == 7 else 0.00,
                    'august': net_fund_position if month_id == 8 else 0.00,
                    'september': net_fund_position if month_id == 9 else 0.00,
                    'october': net_fund_position if month_id == 10 else 0.00,
                    'november': net_fund_position if month_id == 11 else 0.00,
                    'december': net_fund_position if month_id == 12 else 0.00,
                }
                master_table.append(main_line)
            else:
                main_line['january'] += net_fund_position if month_id == 1 else 0.00
                main_line['february'] += net_fund_position if month_id == 2 else 0.00
                main_line['march'] += net_fund_position if month_id == 3 else 0.00
                main_line['april'] += net_fund_position if month_id == 4 else 0.00
                main_line['may'] += net_fund_position if month_id == 5 else 0.00
                main_line['june'] += net_fund_position if month_id == 6 else 0.00
                main_line['july'] += net_fund_position if month_id == 7 else 0.00
                main_line['august'] += net_fund_position if month_id == 8 else 0.00
                main_line['september'] += net_fund_position if month_id == 9 else 0.00
                main_line['october'] += net_fund_position if month_id == 10 else 0.00
                main_line['november'] += net_fund_position if month_id == 11 else 0.00
                main_line['december'] += net_fund_position if month_id == 12 else 0.00

            # Required Funds
            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_4)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_4,
                    'january': required_fund_budget if month_id == 1 else 0.00,
                    'february': required_fund_budget if month_id == 2 else 0.00,
                    'march': required_fund_budget if month_id == 3 else 0.00,
                    'april': required_fund_budget if month_id == 4 else 0.00,
                    'may': required_fund_budget if month_id == 5 else 0.00,
                    'june': required_fund_budget if month_id == 5 else 0.00,
                    'july': required_fund_budget if month_id == 7 else 0.00,
                    'august': required_fund_budget if month_id == 8 else 0.00,
                    'september': required_fund_budget if month_id == 9 else 0.00,
                    'october': required_fund_budget if month_id == 10 else 0.00,
                    'november': required_fund_budget if month_id == 11 else 0.00,
                    'december': required_fund_budget if month_id == 12 else 0.00,
                }
                master_table.append(main_line)
            else:
                main_line['january'] += required_fund_budget if month_id == 1 else 0.00
                main_line['february'] += required_fund_budget if month_id == 2 else 0.00
                main_line['march'] += required_fund_budget if month_id == 3 else 0.00
                main_line['april'] += required_fund_budget if month_id == 4 else 0.00
                main_line['may'] += required_fund_budget if month_id == 5 else 0.00
                main_line['june'] += required_fund_budget if month_id == 6 else 0.00
                main_line['july'] += required_fund_budget if month_id == 7 else 0.00
                main_line['august'] += required_fund_budget if month_id == 8 else 0.00
                main_line['september'] += required_fund_budget if month_id == 9 else 0.00
                main_line['october'] += required_fund_budget if month_id == 10 else 0.00
                main_line['november'] += required_fund_budget if month_id == 11 else 0.00
                main_line['december'] += required_fund_budget if month_id == 12 else 0.00

            # Closing Balance
            existing_lines = (
                line_id for line_id in master_table if
                line_id['particulars'] == particulars_5)
            main_line = next(existing_lines, False)

            if not main_line:
                main_line = {
                    'particulars': particulars_5,
                    'january': closing_balance if month_id == 1 else 0.00,
                    'february': closing_balance if month_id == 2 else 0.00,
                    'march': closing_balance if month_id == 3 else 0.00,
                    'april': closing_balance if month_id == 4 else 0.00,
                    'may': closing_balance if month_id == 5 else 0.00,
                    'june': closing_balance if month_id == 5 else 0.00,
                    'july': closing_balance if month_id == 7 else 0.00,
                    'august': closing_balance if month_id == 8 else 0.00,
                    'september': closing_balance if month_id == 9 else 0.00,
                    'october': closing_balance if month_id == 10 else 0.00,
                    'november': closing_balance if month_id == 11 else 0.00,
                    'december': closing_balance if month_id == 12 else 0.00,
                }
                master_table.append(main_line)
            else:
                main_line['january'] += closing_balance if month_id == 1 else 0.00
                main_line['february'] += closing_balance if month_id == 2 else 0.00
                main_line['march'] += closing_balance if month_id == 3 else 0.00
                main_line['april'] += closing_balance if month_id == 4 else 0.00
                main_line['may'] += closing_balance if month_id == 5 else 0.00
                main_line['june'] += closing_balance if month_id == 6 else 0.00
                main_line['july'] += closing_balance if month_id == 7 else 0.00
                main_line['august'] += closing_balance if month_id == 8 else 0.00
                main_line['september'] += closing_balance if month_id == 9 else 0.00
                main_line['october'] += closing_balance if month_id == 10 else 0.00
                main_line['november'] += closing_balance if month_id == 11 else 0.00
                main_line['december'] += closing_balance if month_id == 12 else 0.00

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
