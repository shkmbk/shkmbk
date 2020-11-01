from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from pytz import timezone
import pytz

class AnnualLeaveReport(models.AbstractModel):
    _name = 'report.mbk_reports.report_annualleave'
    _description = "Annual Leave Report"

    
    @api.model
    def _get_employee(self,employee_id):
        if employee_id:
            return ('employee_id', '=', employee_id)
        else:
            return (1, '=', 1)

    def _get_department(self,hr_department_ids):
        if hr_department_ids:
            return ('department_id', 'in', hr_department_ids)
        else:
            return (1, '=', 1)

    def _get_analytic(self,analytic_id):
        if analytic_id:
            return ('analytic_account_id', '=', analytic_id)
        else:
            return (1, '=', 1)
    def _get_analytic_tags(self,analytic_tag_ids):
        if analytic_tag_ids:
            return ('x_analytic_tag_ids', 'in', analytic_tag_ids)
        else:
            return (1, '=', 1)                 

   
    def _get_report_values(self, docids, data=None):
        self.env['ir.rule'].clear_cache()
        ason_date = data['ason_date']
        employee_id = data['employee_id']
        hr_department_ids = data['hr_department_ids']
        category_ids = data['category_ids']
        analytic_account_id = data['analytic_account_id']
        analytic_tag_ids = data['analytic_tag_ids']
        header_date = data['header_date']

        as_on_date = datetime.strptime(ason_date, '%Y-%m-%d').date()
        

        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))
            
        objemp = self.env['hr.contract'].search([('state', 'in', ['open', 'close']), ('employee_id.date_of_join', '<=', ason_date),self._get_analytic(analytic_account_id),
                                                    self._get_department(hr_department_ids), self._get_analytic_tags(analytic_tag_ids),self._get_employee(employee_id)])

        if not objemp:
            raise UserError('There are no employee found for selected parameters')
            #raise UserError(self._getdomainfilter(from_date,to_date,employee_id,analytic_id))

        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            date = pytz.utc.localize(datetime.now()).astimezone(tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            date = datetime.now()
            time = datetime.now()
        #date_string =  to_date.strftime("%B-%y")

        #report_name = 'Stock_Summary_'+ date.strftime("%y%m%d%H%M%S")
        #filename = '%s %s' % (report_name, date_string)
        
        op_fy_date = datetime(2020, 6, 1).date()
        
        master_table = []
        annualleave_days = 0.0
        annualleave_amount = 0.0
        basic_salary = 0.00
        per_day = 0.00
        eligible_days = 0.00

        for rec in objemp:       
            join_date = rec.employee_id.date_of_join
            contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id), ('date_start', '<=', as_on_date), ('date_end', '>=', as_on_date)])
            if contract:
                basic_salary = contract.wage
                allowances = contract.x_other_allowance
            else:
                basic_salary = rec.wage
                allowances = rec.x_other_allowance

            net_salary = basic_salary+allowances
            per_day = net_salary*12/365
            op_al_days = rec.employee_id.op_leave_days

            #Checking wheather contract end date mentioned
            if rec.date_end:
                to_date = rec.date_end
            else:                
                to_date = as_on_date

            total_days = (to_date-join_date).days+1
            op_eligible_days = rec.employee_id.op_eligible_days



            if join_date<op_fy_date:
                op_lop_days = (op_fy_date-join_date).days-op_eligible_days
                c_total_days = (to_date-op_fy_date).days+1
            else:
                op_lop_days = 0
                c_total_days = (to_date-join_date).days+1

            #LOP Leaves in Currecnt Period
            objlopleave = self.env['hr.leave'].search([('employee_id', '=', rec.employee_id.id),('state', '=', 'validate'),('holiday_status_id.unpaid','=',1),('request_date_from','<=',to_date)])
            c_lop=0.00
            for lop in objlopleave:
                if lop.request_date_to<=to_date:
                    c_lop+=lop.number_of_days
                else:
                    c_lop+=(to_date-lop.request_date_from).days+1
            #Annual Leave Taken
            objalleave = self.env['hr.leave'].search([('employee_id','=',rec.employee_id.id),('state','=','validate'),('holiday_status_id','=',1),('request_date_from','<=',to_date)])
            c_alt=0.00
            for al in objalleave:
                if al.request_date_to<=to_date:
                    c_alt+=al.number_of_days
                else:
                    c_alt+=(to_date-al.request_date_from).days+1

            #Encashed Days
            encashed_days= 0.0
            encashed_amount = 0.00
            objencash = self.env['mbk.encash'].search([('employee_id', '=', rec.employee_id.id),('state', '=', 'done'), ('date_to', '<=', to_date)])
            
            for en in objencash:
                if en.encash_days:
                    encashed_days += en.encash_days
                    encashed_amount += en.encash_amount

            obj_esob = self.env['mbk.esob'].search([('employee_id', '=', rec.employee_id.id), ('state', '!=', 'cancel'), ('date_to', '<=', to_date)])
            for es in obj_esob:
                encashed_days += es.encash_days
                encashed_amount += es.encash_amount
            
            total_leaves = encashed_days+c_alt
            lop_days = op_lop_days+c_lop

            if join_date < op_fy_date:
                eligible_days = op_eligible_days+c_total_days-c_lop
            else:
                eligible_days = c_total_days - c_lop
            c_eligible_days = c_total_days - c_lop

            new_al_days = (c_eligible_days*30/365)
            annualleave_days = round(op_al_days+new_al_days-total_leaves,2)
            annualleave_amount = round(per_day * annualleave_days, 2)

            obj_last_leave_p = self.env['mbk.leave_provision.line'].search(
                [('employee_id', '=', rec.employee_id.id), ('leave_provision_id.state', '=', 'posted'), ('to_date', '<=', as_on_date)],
                order='to_date desc', limit=1)

            last_leave_pb_date = obj_last_leave_p.to_date
            provision_bal_amount = obj_last_leave_p.avl_leave_amount

            if last_leave_pb_date:
                last_leave_pb_date_str = last_leave_pb_date.strftime("%d-%m-%Y")
            else:
                last_leave_pb_date_str = False

            # Computing total booked Leave Salary provision
            obj_ls_provision = self.env['mbk.leave_provision.line'].search(
                [('employee_id', '=', rec.employee_id.id), ('leave_provision_id.state', '=', 'posted'), ('to_date', '<=', as_on_date)])
            lsp_booked = 0.00
            for lsp in obj_ls_provision:
                lsp_booked += lsp.amount

            net_leave_amount = lsp_booked - encashed_amount

            master_table.append({
                            'emp_name': rec.employee_id.name,
                            'emp_code': rec.employee_id.registration_number,
                            'join_date': join_date.strftime("%d-%m-%Y"),
                            'net_salary': net_salary,
                            'total_days': total_days,
                            'lop_days': lop_days,
                            'eligible_days': eligible_days,
                            'opening_days': op_al_days,
                            'new_days': new_al_days,
                            'leave_taken': c_alt,
                            'encash': encashed_days,
                            'balanceal_days': annualleave_days,
                            'annualleave_amount': annualleave_amount,
                            'provision_date': last_leave_pb_date_str,
                            'provision_amount': net_leave_amount,
                        })
        master_table.sort(key=lambda g:(g['annualleave_amount'],g['eligible_days']), reverse=True)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.employee',
            'docs': master_table,
            'to_date': header_date,
        }
        return docargs