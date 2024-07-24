from odoo import http
from odoo.http import request


class PatientForm(http.Controller):

    @http.route('/patient', type='http', website=True, auth='public')
    def patient_form(self):
        return request.render("hospital.patient_form_template")

    @http.route('/create_patient', type='http', website=True, auth='public')
    def create_patient_record(self, **kwargs):
        if kwargs:
            try:
                kwargs.update({'gender': kwargs['gender'].lower()})
                request.env['hospital.patient'].sudo().create(kwargs)
            except ValueError:
                kwargs.pop('gender')
                request.env['hospital.patient'].sudo().create(kwargs)
            return request.render("hospital.contactus_thanks")
