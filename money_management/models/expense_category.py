from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class ExpenseCategory(models.Model):
    _name = "expense.category"
    _rec_name = 'name'
    _description = "expense.category"
    _order = 'name'

    name = fields.Char(string='Expense Category', required=True)
    is_income = fields.Boolean('Is Income?', default=False)
    expense_ids = fields.One2many('expense.transaction', 'category', 'Transaction from this Category', readonly=True)
