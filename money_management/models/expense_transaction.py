from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class ExpenseTransaction(models.Model):
    _name = "expense.transaction"
    _rec_name = 'name'
    _description = "expense.transaction"
    _order = 'name'

    name = fields.Char('Expense', required=True, copy=False)
    category = fields.Many2one('expense.category', string='Category', required=True,
                               domain=[('is_income', '!=', True)], ondelete='cascade',)
    amount = fields.Integer('Amount', required=True, copy=False)
    total_expense = fields.Integer('Total', invisible=True, compute='_total_expense')
    total_needs = fields.Integer('Needs', invisible=True, compute='_total_expense')
    total_wants = fields.Integer('Wants', invisible=True, compute='_total_expense')
    expense_type = fields.Selection([('need', 'Need'), ('want', 'Want')], default='want', required=True)
    note = fields.Text('Note', default='Notes are not available')
    date = fields.Date('Transaction Date', default=lambda self: fields.Datetime.now(), copy=False)

    @api.constrains('amount')
    def expense_amount_check(self):
        if self.amount <= 0:
            raise ValidationError(_('Amount can not be zero for transaction'))

    def _total_expense(self):
        total_expense = self.search([('amount', '!=', False)])
        total_needs = total_expense.filtered(lambda i: i.expense_type == 'need')
        total_wants = total_expense.filtered(lambda i: i.expense_type == 'want')
        self.total_expense = sum(total_expense.mapped('amount'))
        self.total_needs = sum(total_needs.mapped('amount'))
        self.total_wants = sum(total_wants.mapped('amount'))


