from odoo import fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import calendar


class PLReportWizard(models.TransientModel):
    _name = 'mbk.pl.wizard'
    _description = 'Profit & Loss Report'

    year = fields.Selection([(str(num), str(num)) for num in range(2020, (datetime.now().year) + 2)], default=str(datetime.now().year),
                            required="1")
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], string='Month', default=str((date.today() + relativedelta(months=-1)).month), required="1")
    analytic_id = fields.Selection([('0', 'All'), ('9', 'Al Dhafra Workers Village'), ('10', 'Al Dhafra Property Management'), ('11', 'MBK Securities'), ('12', 'Royal M Hotel Abu Dhabi'), ('13', 'Royal M Hotel Fujairah'), ('14', 'Up Town Hotel Apartments - Abu Dhabi'), ('15', 'Up Town Hotel Apartments - Fujairah'), ('16', 'Fujairah Mall'), ('17', 'Galaxy Cinemas'), ('18', 'Shoot & Cart'), ('19', 'MBK Marine Industries')], string='Division', default='0', required="1")
    is_detailed = fields.Boolean(string="Detailed Report", default=False)

    def button_export_pdf(self):
        if self.analytic_id != '0':
            # First fetch the dictionary with key-value pair that was defined in your field
            kay_val_dict = dict(self._fields['analytic_id'].selection)  # here 'type' is field name
            # Now iterate loop for all pair of key-val and based on that you can set label
            for key, val in kay_val_dict.items():
                if key == self.analytic_id:
                    header_name = val
        else:
            header_name = 'MBK GROUP OF COMPANIES'

        data = {'year': self.year, 'month': self.month, 'is_detailed': self.is_detailed,
                'header_name': header_name.upper(), 'analytic_id': int(self.analytic_id)}
        report = self.env.ref('mbk_reports.pl_report_pdf')
        return report.report_action(self, data=data)

    def button_summary(self):
        header_period = calendar.month_name[int(self.month)] + ' ' + self.year
        data = {'year': self.year, 'month': self.month, 'is_detailed': self.is_detailed,
                'header_period': header_period.upper()}
        report = self.env.ref('mbk_reports.pl_group_report')
        return report.report_action(self, data=data)
