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
    'name': 'MIS-AUH Report',
    'version': '13.0.0.1',
    'summary': """Mis Report""",
    'category': 'Report',
    'author': 'Hafeel Salim, hafeel.salim@gmail.com',
    'company': 'mindinfosys.com, UAE',
    'description': 'Report Customization',
    'website': 'www.mindinfosys.com',
    'depends': ['base', 'account'],
    'data': [
        'reports/invoice_report_templates.xml',
        'reports/report_list.xml',
        'reports/purchase_report_templates.xml',
        'reports/sale_template.xml',
        'reports/payment_report_template.xml',
        'reports/journal_report_templates.xml',
        'reports/pettycash_report_templates.xml',
        'views/account_grouptype_views.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}