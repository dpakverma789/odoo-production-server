from odoo import api, exceptions, fields, models, _


class GymMembershipPlan(models.Model):
    _name = "gymwale.membership_plan"
    _description = "GymWale Membership Plan"
    _rec_name = "membership"
    # _order = "membership"

    membership = fields.Char('Membership')
    membership_amount = fields.Integer('Membership Amount')
    membership_period = fields.Integer('Membership Period')
