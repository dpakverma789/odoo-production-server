from odoo import api, fields, models, tools, _


class PatientClassStatus(models.Model):
    _name = "patient.class.status"
    _description = "patient.class.status"
    _rec_name = "patient_class_status"

    patient_class_status = fields.Char('Patient Class Status')
    color = fields.Integer('Color Index')

    _sql_constraints = [('positive_color', 'CHECK(color >= 0)', 'The color code must be positive !')]

