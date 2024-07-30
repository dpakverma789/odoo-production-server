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

    power_unit_cost = fields.Float('Power Unit Cost')
    power_consume = fields.Float('Power Consume', tracking=True)
    light_bill_amount = fields.Integer('Light Bill Amount', compute='compute_light_water_bill_amount')

    number_of_water_bottles = fields.Integer('Number of Water Bottles', tracking=True)
    bottle_unit_cost = fields.Float('Bottle Unit Cost')
    water_bill_amount = fields.Integer('Water Bill Amount', compute='compute_light_water_bill_amount')

    gym_hall_rent = fields.Integer('Gym Hall Rent')
    other_service_bill = fields.Integer('Other Service', compute='_compute_other_service_bill')
    remarks = fields.Text('Remarks')
    total_expense = fields.Integer('Total Expense', compute='compute_total_expense')
    total_expense_old = fields.Integer('Total Expense')

    def _compute_other_service_bill(self):
        for rec in self:
            rec.other_service_bill = 0
            if rec.remarks:
                total = sum([int(x) for x in re.findall(r'\d+', rec.remarks)])
                rec.other_service_bill = total if total else 0

    @api.depends('light_bill_amount', 'water_bill_amount', 'gym_hall_rent', 'other_service_bill')
    def compute_total_expense(self):
        bill_source = ('light_bill_amount', 'water_bill_amount', 'gym_hall_rent', 'other_service_bill')
        dashboard = self.env['gymwale.dashboard'].search([], limit=1)
        for rec in self:
            total = [rec.mapped(i)[0] for i in bill_source]
            rec.total_expense = sum(total) if total else False
            if rec.total_expense_old != rec.total_expense:
                dashboard.in_balance_collection -= rec.total_expense - rec.total_expense_old
                rec.total_expense_old = rec.total_expense

    @api.depends('power_consume', 'power_unit_cost', 'bottle_unit_cost', 'number_of_water_bottles')
    def compute_light_water_bill_amount(self):
        for rec in self:
            rec.light_bill_amount = rec.water_bill_amount = 0.0
            if rec.power_consume and rec.power_unit_cost:
                rec.light_bill_amount = rec.power_consume * rec.power_unit_cost
            if rec.bottle_unit_cost and rec.number_of_water_bottles:
                rec.water_bill_amount = rec.bottle_unit_cost * rec.number_of_water_bottles