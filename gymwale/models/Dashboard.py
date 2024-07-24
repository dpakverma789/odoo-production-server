from odoo import api, exceptions, fields, models, _


class Dashboard(models.Model):
    _name = "gymwale.dashboard"
    _description = "GymWale dashboard"

    total_paid_members = fields.Integer('Total Paid Members', compute='compute_total_paid_members')
    total_amount_collected = fields.Integer('Total Amount Collected', compute='compute_total_amount_collected')
    total_gym_expense = fields.Integer('Total GYM Expense', compute='compute_total_gym_expense')
    total_collection = fields.Integer('Total Collection')
    net_collection = fields.Integer('Net Collection', compute='compute_net_collection')
    monthly_collection = fields.Integer('Monthly Collection', compute='compute_monthly_collection')

    def compute_monthly_collection(self):
        arg = []
        all_paid_members = self.env['gymwale.members'].search([('is_amount_paid', '=', True)])
        monthly_members_total = sum(all_paid_members.filtered(lambda x: x.amount_to_be_paid <= 700).mapped('amount_to_be_paid'))
        quarterly_members_total = sum(all_paid_members.filtered(lambda x: 700 < x.amount_to_be_paid <= 1800).mapped('amount_to_be_paid'))
        half_yearly_members_total = sum(all_paid_members.filtered(lambda x: 1800 < x.amount_to_be_paid <= 3000).mapped('amount_to_be_paid'))
        annual_members_total = sum(all_paid_members.filtered(lambda x: 3000 < x.amount_to_be_paid).mapped('amount_to_be_paid'))
        if monthly_members_total:
            arg.append(monthly_members_total)
        if quarterly_members_total:
            arg.append(quarterly_members_total//3)
        if half_yearly_members_total:
            arg.append(half_yearly_members_total//6)
        if annual_members_total:
            arg.append(annual_members_total//12)
        self.monthly_collection = sum(arg) if arg else 0

    @api.depends('monthly_collection', 'total_gym_expense')
    def compute_net_collection(self):
        for rec in self:
            rec.net_collection = rec.monthly_collection - rec.total_gym_expense

    def compute_total_paid_members(self):
        total_paid_members = self.env['gymwale.members'].search_count([('is_amount_paid', '=', True)])
        for rec in self:
            rec.total_paid_members = total_paid_members if total_paid_members else 0

    def compute_total_amount_collected(self):
        total_paid_members = self.env['gymwale.members'].search([('is_amount_paid', '=', True)])
        self.total_amount_collected = 0.0
        if total_paid_members:
            for rec in self:
                collection = total_paid_members.mapped('amount_to_be_paid')
                total_collection = sum(collection)
                rec.total_amount_collected = total_collection if total_collection else 0

    def compute_total_gym_expense(self):
        total_expense_records = self.env['gymwale.expense'].search([], order='bill_from desc', limit=1)
        for rec in total_expense_records:
            self.total_gym_expense = rec.total_expense
