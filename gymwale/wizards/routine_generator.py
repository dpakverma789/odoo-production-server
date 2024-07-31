
from odoo import api, exceptions, fields, models, _
from datetime import timedelta


class AppointmentRequestWizard(models.TransientModel):
    _name = "gymwale.routine_generator.wizard"
    _description = "gymwale Routine Generator"

    routine = fields.Text('Routine')
    member_id = fields.Many2one('gymwale.members', string='Member')
    membership_expire = fields.Date('Membership expire', related='member_id.membership_expire')
    last_date = fields.Date('Last Date')