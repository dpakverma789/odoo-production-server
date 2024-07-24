from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class CreditCardManager(models.Model):
    _name = "credit.card.manager"
    _rec_name = 'name'
    _description = "credit.card.manager"
    _order = 'name'

    name = fields.Char(string='Expense', required=True)
    bank_card_id = fields.Many2one('expense.bank.card', 'Bank Card')
    currency_id = fields.Many2one('res.currency', string='Amount Currency')
    amount = fields.Monetary(string='Amount Due', copy=False)
    due_date = fields.Date('Due Date', required=True)
    paid_date = fields.Datetime('Paid Date', default=lambda self: fields.Datetime.now(), copy=False)
    payment_state = fields.Selection([('pending', "Pending"), ('done', 'Completed')],
                                     string="Payment Status", default='pending', copy=False)

    @api.constrains('amount')
    def expense_amount_check(self):
        if self.amount <= 0:
            raise ValidationError(_('Amount can not be zero for transaction'))

    def unlink(self):
        for rec in self:
            if rec.payment_state == 'done':
                raise ValidationError(_('Can not Delete Paid Bill'))
        return super(CreditCardManager, self).unlink()

    def confirm_payment(self):
        self.env['expense.transaction'].create({
            'name': self.name,
            'category': self.env['expense.category'].search([('name', '=', 'Credit Card Bills')]).id,
            'amount': self.amount,
            'date': self.paid_date,
            'expense_type': 'need'
        })
        self.payment_state = 'done'
