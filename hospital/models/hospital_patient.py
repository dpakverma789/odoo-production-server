
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _rec_name = 'name'
    _description = "hospital.patient"
    _order = 'name'

    name = fields.Char('Patient Name', required=True, default=lambda self: self.env.user.name)
    image = fields.Binary("Image", copy=False)
    age = fields.Integer('Patient Age', default=10)
    contact = fields.Char('Patient Contact', required=True, copy=False)
    email = fields.Char('Patient Email', copy=False)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], required=True)
    appointment_ids = fields.One2many('hospital.appointment', inverse_name='patient_id',
                                      string='Appointments', readonly=True)
    patient_class_status_ids = fields.Many2many('patient.class.status', 'appointment_patient_status_rel',
                                                'appointment_id', 'patient_status_id', string='Patient Status',
                                                required=True)
    hide_rejection_reason = fields.Boolean('Hide Rejection Reason')

    _sql_constraints = [('patient_contact_unique', 'unique(contact, email)',
                         'Patient can not have same contact or email'),
                        ('patient_age_check', 'check(age > 0)', 'Patient age should be more than zero')]

    def copy(self, default=None):
        default = dict(default or {})
        default.update(name=_("%s (copy)") % (self.name or ''))
        return super(HospitalPatient, self).copy(default)

    # @api.constrains('name')
    # def _check_patient_contact(self):
    #     patient_contact = self.search([('contact', '=', self.contact), ('id', '!=', self.id),
    #                                    ('contact', '!=', 'False')])
    #     if patient_contact:
    #         raise ValidationError(_('You cannot create patient with same contact.'))
