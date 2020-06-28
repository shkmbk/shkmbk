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
    'name': 'MIS-AUH Partner',
    'version': '13.0.0.1',
    'summary': """Partner Modification""",
    'category': 'Partner',
    'author': 'Hafeel Salim, hafeel.salim@gmail.com',
    'company': 'mindinfosys.com, UAE',
    'description': 'Partner Customization',
    'website': 'www.mindinfosys.com',
    'depends': ['base','account', 'account_accountant','analytic',],
    'data': [
        'views/mis_partner.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}