
from odoo import fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError


class ShareRevaluationReport(models.TransientModel):
    _name = 'mis.auh.revaluation.wizard'
    _description = 'Share Revaluation Report'

    date_from = fields.Date(default=fields.Date.to_string(date.today()), required="1")
    date_to = fields.Date(default=fields.Date.to_string(date.today()), required="1")
    classification_id = fields.Many2one('mis.inv.classfication', string="Classification")
    status = fields.Selection([('All', 'All'), ('Active', 'Active'), ('Inactive', 'Inactive')], default='All', required="1")


    def button_export_pdf(self):
        data = {}

        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        tmpdate = self.date_to

        data['status'] = self.status
        data['classification'] = self.classification_id.id
        data['header_date'] = tmpdate.strftime("%d-%m-%Y")
        report = self.env.ref(
            'mis_investment.action_share_revalution_report')
        return report.report_action(self, data=data)

