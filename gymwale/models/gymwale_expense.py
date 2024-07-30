from odoo import api, exceptions, fields, models, _
import re


class GymExpense(models.Model):
    _name = "gymwale.expense"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "GymWale Expense"
    _rec_name = 'bill_from'
    _order = 'id desc'

    bill_from = fields.Date('Bill From')
    bill_to = fields.Date('Bill To')
    light_bill_amount = fields.Integer('Light Bill Amount')
    water_bill_amount = fields.Integer('Water Bill Amount')
    gym_hall_rent = fields.Integer('Gym Hall Rent')
    other_service_bill = fields.Integer('Other Service', compute='_compute_other_service_bill')
    remarks = fields.Text('Remarks')
    total_expense = fields.Integer('Total Expense', compute='compute_total_expense')
    created_by = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user)

    def _compute_other_service_bill(self):
        for rec in self:
            rec.other_service_bill = 0
            if rec.remarks:
                total = sum([int(x) for x in re.findall(r'\d+', rec.remarks)])
                rec.other_service_bill = total if total else 0

    @api.depends('light_bill_amount', 'water_bill_amount', 'gym_hall_rent', 'other_service_bill')
    def compute_total_expense(self):
        bill_source = ('light_bill_amount', 'water_bill_amount', 'gym_hall_rent', 'other_service_bill')
        for rec in self:
            total = [rec.mapped(i)[0] for i in bill_source]
            rec.total_expense = sum(total) if total else False