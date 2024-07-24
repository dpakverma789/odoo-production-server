from odoo import api, fields, models, tools, _


class CreditCardManager(models.Model):
    _name = "expense.bank.card"
    _rec_name = 'name'
    _description = "expense.bank.card"
    _order = 'name'

    name = fields.Char('Bank Name')
