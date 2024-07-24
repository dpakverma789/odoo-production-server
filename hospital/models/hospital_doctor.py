
from odoo import api, fields, models, tools, _


class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _rec_name = 'name'
    _description = "hospital.doctor"
    _order = 'name'

    name = fields.Char('Doctor Name', required=True)
    image = fields.Binary("Image")
    specialization = fields.Char('Specialization', required=True)
    active = fields.Boolean('Active', default=True)
    total_appointment = fields.Integer('Total Appointment')
    patient_appointment_ids = fields.One2many('hospital.appointment', inverse_name='doctor_id',
                                              string='Appointments', readonly=True)

    @staticmethod
    def total_appointment_count(doctor_id):
        """
        this static function checks the total appointment count of the doctor and store the count to
        variable total appointment. this function gets trigger when appointment confirm button is clicked
        :param doctor_id:
        :return:
        """
        if doctor_id and doctor_id.patient_appointment_ids:
            appointment_count = doctor_id.patient_appointment_ids.filtered(lambda i: i.appointment_state == 'Confirmed')
            if appointment_count:
                doctor_id.total_appointment = len(appointment_count.ids) if appointment_count else 0
                return

    def copy(self, default=None):
        default = dict(default or {})
        default.update(name=_("%s (copy)") % (self.name or ''))
        return super(HospitalDoctor, self).copy(default)

