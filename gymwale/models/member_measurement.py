from odoo import api, exceptions, fields, models, _


class MemberMeasurement(models.Model):
    _name = "member.measurement"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Member Measurement"
    _rec_name = 'member_id'

    height = fields.Char('Height')
    weight = fields.Integer('Weight')
    shoulder = fields.Integer('Shoulder')
    chest = fields.Char('Chest')
    biceps = fields.Char('Biceps')
    waist = fields.Char('Waist')
    thigh = fields.Char('Thigh')
    measurement_date = fields.Date('Measurement Date')
    member_id = fields.Many2one('gymwale.members', string='Member')
