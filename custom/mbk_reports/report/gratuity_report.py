from odoo import models, api
from datetime import timedelta, datetime, date
from odoo.exceptions import ValidationError, UserError
from pytz import timezone
import pytz

class GratuityReport(models.AbstractModel):
    _name = 'report.mbk_reports.report_gratuity'
    _description = "Gratuity Report"

    
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
        employee_id =data['employee_id']
        hr_department_ids = data['hr_department_ids']
        category_ids=data['category_ids']
        analytic_account_id=data['analytic_account_id']
        analytic_tag_ids = data['analytic_tag_ids']
        header_date = data['header_date']

        as_on_date= datetime.strptime(ason_date, '%Y-%m-%d').date()
        

        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))
            
        objemp = self.env['hr.contract'].search([('state', '=', 'open'),('employee_id.date_of_join', '<=', ason_date),self._get_analytic(analytic_account_id),
                                                    self._get_department(hr_department_ids), self._get_analytic_tags(analytic_tag_ids),self._get_employee(employee_id)])

        if not objemp:
            raise UserError('There are no stock found for selected parameters')
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
        
        master_table =[]
        gratuity_days=0.0
        gratuity_amount=0.0
        basic_salary=0.00
        per_day=0.00
        eligible_days=0.00

        for rec in objemp:       
            join_date=rec.employee_id.date_of_join
            basic_salary=rec.wage
            per_day=basic_salary*12/365
            #Checking wheather contract end date mentioned
            if rec.date_end:
                to_date=rec.date_end
            else:                
                to_date=as_on_date

            total_days=(to_date-join_date).days+1
            op_eligible_days=rec.employee_id.op_eligible_days



            if join_date<op_fy_date:
                op_lop_days=(op_fy_date-join_date).days-op_eligible_days
                c_total_days=(to_date-op_fy_date).days+1
            else:
                op_lop_days=0
                c_total_days=(to_date-join_date).days+1

            objlopleave = self.env['hr.leave'].search([('employee_id','=',employee_id),('state','=','validate'),('holiday_status_id.unpaid','=',1),('request_date_from','<=',to_date)])
            c_lop=0.00
            for lop in objlopleave:
                if lop.request_date_to<=to_date:
                    c_lop+=lop.number_of_days
                else:
                    c_lop+=(to_date-lop.request_date_from).days+1
            lop_days=op_lop_days+c_lop

            if join_date<op_fy_date:                
                eligible_days= op_eligible_days+c_total_days-c_lop
            else:
                eligible_days=c_total_days-c_lop

            if eligible_days<365:
                gratuity_days=0.00
                gratuity_amount=0.00
            elif eligible_days>=365 and eligible_days<1825:
                gratuity_days=eligible_days*21/365
            else:
                gratuity_days=round(105+((eligible_days-1825)*30/365),2)
            
            gratuity_amount= round(per_day*gratuity_days,2)

                        
            master_table.append({
                            'emp_name': rec.employee_id.name,
                            'emp_code': rec.employee_id.registration_number,
                            'join_date':join_date.strftime("%d-%m-%Y"),
                            'basic_salary': basic_salary,
                            'total_days': total_days,
                            'lop_days': lop_days,
                            'eligible_days': eligible_days,
                            'gratuity_days' : gratuity_days,
                            'gratuity_amount' : gratuity_amount,
                        })
        master_table.sort(key=lambda g:(g['gratuity_amount'],g['eligible_days']), reverse=True)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': 'hr.employee',
            'docs': master_table,
            'to_date': header_date,
        }
        return docargs