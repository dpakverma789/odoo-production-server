from odoo import api, exceptions, fields, models, _


class GymMembershipPlan(models.Model):
    _name = "gymwale.membership_plan"
    _description = "GymWale Membership Plan"
    _rec_name = "membership"
    _order = "membership_amount"

    membership = fields.Selection([('Monthly', 'Monthly'), ('Quarterly', 'Quarterly'), ('Half Yearly', 'Half Yearly'),
                                   ('Annual', 'Annual')], string='Membership', default='Monthly')
    membership_amount = fields.Integer('Membership Amount')
    membership_period = fields.Integer('Membership Period (in days)')
    created_by = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user)

    _sql_constraints = [('unique_membership', 'unique (membership)', "Membership Plan already exists !"),
                        ('unique_amount', 'CHECK(membership_amount>0)', "Membership Amount Can not be Zero !"),
                        ('unique_period', 'CHECK(membership_period>0)', "Membership Period Can not be Zero !")]



