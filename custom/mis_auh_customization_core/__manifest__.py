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
    'name': 'MIS-AUH Customization Core',
    'version': '13.0.0.1',
    'summary': """Adding Advanced Fields In core modules""",
    'category': 'Accounting',
    'author': 'Hafeel Salim, hafeel.salim@gmail.com',
    'company': 'mindinfosys.com, UAE',
    'description': 'Core Customization',
    'website': 'www.mindinfosys.com',
    'depends': ['base','account', 'purchase', 'sale', 'account_asset', 'analytic','stock',],
    'data': [
        'data/account_payment_method_data.xml',
        'views/mis_accounts.xml',
        'views/mis_account_journal.xml',
        'views/mis_account_anlytic.xml',
        'views/mis_invoice.xml',
        'views/mis_purchaseorder.xml',
        'views/mis_saleorder.xml',
        'views/mis_partner.xml',
#        'views/mis_assets.xml',
#        'views/mis_auh_bank.xml',
        'views/mis_auh_payment.xml',
        'views/mis_auh_stockpicking.xml',
       'security/ir.model.access.csv',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}