from odoo import api, fields, models, tools, _


class ExpenseCategory(models.Model):
    _name = "income.source"
    _rec_name = 'name'
    _description = "income.source"
    _order = 'name'

    name = fields.Char(string='Income Source', required=True)
    expense_ids = fields.One2many('expense.transaction', 'category', 'Transaction from this Category', readonly=True)
