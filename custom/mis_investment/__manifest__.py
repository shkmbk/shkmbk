#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

{
    'name': 'MIS-Auh-Investment',
    'version': '13.0.0.1',
    'summary': """New functionality Investment vertical""",
    'category': 'Accounting',
    'author': 'Hafeel Salim, hafeel.salim@gmail.com',
    'company': 'mindinfosys.com, UAE',
    'description': 'Investment 13.0',
    'website': 'www.mindinfosys.com',
    'depends': ['base','account', 'account_asset', 'analytic'],
    'data': [
        'data/investment_data.xml',
        'data/budget_data.xml',
        'security/ir.model.access.csv',
        'views/investment_view.xml',
        'views/investment_transaction_view.xml',
        'views/mbk_budget_view.xml',
        'views/masters.xml',
        'views/classification_views.xml',
        'views/riskrate_views.xml',
        'views/liquidityreturn _views.xml',
        'views/geographic_views.xml',
        'views/projects_views.xml',
        'report/report_menu.xml',
        'report/share_revaluation_template.xml',
        'report/mc_share_revaluation_template.xml',        
        'report/mc_bond_summary_template.xml',
        'wizard/fd_summaryreport_wizard.xml',
        'wizard/share_revaluation_report_wizard.xml',
        'wizard/mc_share_revaluation_report_wizard.xml',
        'wizard/mc_bond_summary_report_wizard.xml',
        'report/report_papert_format.xml',
        'report/fd_report_template.xml',
        'report/bond_report_template.xml',
        'report/budget_template.xml',
        'wizard/bond_summaryreport_wizard.xml',
        'wizard/budget_report_wizard.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}