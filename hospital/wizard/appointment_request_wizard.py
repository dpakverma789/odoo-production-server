
from odoo import models, fields, api
from datetime import datetime, timedelta


class AppointmentRequestWizard(models.TransientModel):
    _name = 'hospital.appointment.request.wizard'

    rejection_reason = fields.Many2one('appointment.rejection.reason', 'Rejection Reason', required=True)

    def reject_appointment(self):
        rejection_id = self.env['hospital.appointment'].browse(self._context.get("active_id"))
        if rejection_id:
            rejection_id.write({'rejection_id': self.rejection_reason, 'appointment_state': 'Rejected'})
        else:
            discard_appointments = self.env['hospital.appointment'].search([('appointment_state', '=', 'Draft')])
            rejection_reason = self.env['appointment.rejection.reason']\
                .search([('rejection_reason', '=', 'Discard by Bot')])
            for rec in discard_appointments:
                discard_days = int(self.env['ir.config_parameter'].sudo().get_param('discard_days'))
                if discard_days:
                    if rec.create_date + timedelta(days=discard_days) < datetime.now():
                        rec.write({'rejection_id': rejection_reason.id, 'appointment_state': 'Rejected'})
