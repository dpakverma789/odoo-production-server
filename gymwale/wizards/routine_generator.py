
from odoo import api, exceptions, fields, models, _


class AppointmentRequestWizard(models.TransientModel):
    _name = "gymwale.routine_generator.wizard"
    _description = "gymwale Routine Generator"

    routine = fields.Text('Routine')

