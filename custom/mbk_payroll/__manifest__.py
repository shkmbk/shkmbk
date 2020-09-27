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
    'name': 'mbk_payroll',
    'version': '13.0.0.1',
    'summary': """New functionality of Human Resource module as per the company requirements""",
    'category': 'HR',
    'author': 'Rinto Antony',
    'company': 'MBK Group',
    'description': 'MBK Payroll 1.0',
    'website': 'www.mbkgroup.com',
    'depends': ['base','account', 'hr_payroll', 'analytic'],
    'data': [
        'views/mbk_encash_view.xml',
        'security/ir.model.access.csv',
        'data/mbk_encash_sequence.xml',
        'data/mbk_esob_sequence.xml',
        'report/report_list.xml',
        'report/encash_report_templates.xml',
        'report/esob_report_templates.xml',
        'views/mbk_esob_view.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}