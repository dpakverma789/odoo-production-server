
from odoo import api, fields, models, tools, _


class AppointmentRejectionReason(models.Model):
    _name = 'appointment.rejection.reason'
    _rec_name = 'rejection_reason'
    _order = 'rejection_reason desc'

    rejection_reason = fields.Char('Rejection Reason')

    def copy(self, default=None):
        default = dict(default or {})
        default.update(rejection_reason=_("%s (copy)") % self.rejection_reason or '')
        return super(AppointmentRejectionReason, self).copy(default)


