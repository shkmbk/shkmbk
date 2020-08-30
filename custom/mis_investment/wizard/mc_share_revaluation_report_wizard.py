
from odoo import fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError


class ShareMCRevaluationReport(models.TransientModel):
    _name = 'mis.auh.mcrevaluation.wizard'
    _description = 'Multi Currency Share Revaluation Report'

    date_from = fields.Date(default='2020-06-01', required="1", )
    date_to = fields.Date(default=fields.Date.to_string(date.today()), required="1")
    classification_id = fields.Many2one('mis.inv.classfication', string="Classification")
    inv_currency_id = fields.Many2one('res.currency', string="Currency",required="1")
    status = fields.Selection([('All', 'All'), ('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', required="1")


    def button_export_pdf(self):
        data = {}

        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        tmpdate = self.date_to

        data['status'] = self.status
        data['classification'] = self.classification_id.id
        data['currency'] = self.inv_currency_id.id
        data['header_date'] = tmpdate.strftime("%d-%m-%Y")
        report = self.env.ref(
            'mis_investment.action_mc_share_revalution_report')
        return report.report_action(self, data=data)

