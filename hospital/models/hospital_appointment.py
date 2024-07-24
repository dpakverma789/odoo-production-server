import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'patient_id'
    _description = "hospital.appointment"
    _order = 'name desc'

    image = fields.Binary("Image")
    name = fields.Char('Appointment', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    gender = fields.Char('Gender')
    patient_id = fields.Many2one('hospital.patient', 'Patient Name', required=True)
    patient_class_status_ids = fields.Many2many(related='patient_id.patient_class_status_ids')
    patient_description = fields.Text('Description')
    patient_medicine = fields.Text('Medicine')
    doctor_id = fields.Many2one('hospital.doctor', 'Doctor Name', required=True)
    specialization = fields.Char('Specialization', related='doctor_id.specialization')
    appointment_time = fields.Datetime('Appointment Time', required=True)
    appointment_state = fields.Selection([('Draft', "Draft"), ('Confirmed', "Confirmed"), ('Done', 'Done'),
                                          ('Rejected', "Rejected"), ('Expired', 'Expired')],
                                         string="Appointment Status", default='Draft')
    rejection_id = fields.Many2one('appointment.rejection.reason', 'Rejection Reason', readonly=True)
    send_email = fields.Boolean(string='Send Email')

    # Send appointment on whatsapp
    def send_appointment_on_whatsapp(self):
        """
        this function send whatsapp message
        :return: call whatsapp api
        """
        text = f'Hi {self.patient_id.name}'
        whatsapp_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.patient_id.contact, text)
        send = {
            'type': 'ir.actions.act_url',
            'name': "Shipment Tracking Page",
            'target': 'new',
            'url': whatsapp_url,
        }
        return send

    # confirms the appointment
    def confirm_appointment(self):
        """
        this function confirms the appointment of the patient with a selected doctor and check
        if the selected doctor has already appointment or not in the given time slot
        :return:
        """
        all_appointment_ids = self.search([('id', '!=', self.id), ('appointment_state', '=', 'Confirmed'),
                                           ('doctor_id', '=', self.doctor_id.id)])
        if all_appointment_ids:
            for rec in all_appointment_ids:
                conditions = (self.appointment_time > rec.appointment_time + timedelta(minutes=15),
                              rec.appointment_time < self.appointment_time - timedelta(minutes=15))
                if not all(conditions):
                    raise ValidationError(_('Dr. %s Already have Appointment! Try 15 min Later' % self.doctor_id.name))
            del all_appointment_ids, conditions
        self.appointment_state = 'Confirmed'
        self.env['hospital.doctor'].total_appointment_count(self.doctor_id)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'This Appointment is Confirmed!',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }}

    # check past date appointment booking
    @api.constrains('appointment_time')
    def _check_appointment_date(self):
        """
        this function blocks the appointment booking if selected date is in the past
        :return:
        """
        if self.appointment_time < datetime.now():
            raise ValidationError(_('Make an Appointment for Future date!'))

    # overriding delete function to check condition before deleting records
    def unlink(self):
        """
        this function checks if the booking is confirmed it blocks the appointment deletion
        :return:
        """
        for rec in self:
            if rec.appointment_state == 'Confirmed':
                raise ValidationError(_('Can not Delete Confirmed Appointment'))
        return super(HospitalAppointment, self).unlink()

    # overriding create method [vals are all fields from current model]
    @api.model
    def create(self, vals):
        """
        this function generates the unique appointment ids for each new appointment created
        :param vals:
        :return:
        """
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')
        res = super(HospitalAppointment, self).create(vals)
        return res

    # printing report and send email
    def print_patient_appointment_card(self):
        """
        this function send appointment email template when send email is true and
        download pdf appointment template
        :return:
        """
        for rec in self:
            email_template_id = self.env.ref('hospital.patient_appointment_email_template').id
            if email_template_id and rec.send_email:
                rec.env['mail.template'].browse(email_template_id).send_mail(rec.id, force_send=True)
                rec.send_email = False
            return self.env.ref('hospital.patient_appointment_report').report_action(rec)

    # onchange function which depends on patient_id to change patient gender
    @api.onchange('patient_id')
    def _onchange_gender(self):
        """
        this function updates the patient gender and image as per the patient selection
        :return:
        """
        if self.patient_id and self.patient_id.gender:
            self.gender = self.patient_id.gender
            if self.patient_id.image:
                self.image = self.patient_id.image

    # expires the confirm appointment
    def expire_appointment(self):
        """
        this function expires the confirmed appointments once appointment date has been passed
        :return:
        """
        total_appointment = self.search([('appointment_state', '=', 'Confirmed')])
        for rec in total_appointment:
            if rec.appointment_time < datetime.now():
                rec.write({'appointment_state': 'Expired'})

    # wizard call using python function
    def rejection_reason_wizard(self):
        """
        its a rejection reason popup function
        :return:
        """
        wizard_view = {
            'name': _('Rejection Reason'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'hospital.appointment.request.wizard',
            'view_id': self.env.ref('hospital.hospital_appointment_request_wizard').id,
            'target': 'new',
        }
        return wizard_view

    # update image cron
    def update_image(self):
        """
        this function updates the patient image in appointment table if patient image is updated on patient table
        :return:
        """
        records_ids = self.search([])
        not_sync_img = records_ids.filtered(lambda x: x.image != x.patient_id.image)
        if not_sync_img:
            for rec in not_sync_img:
                rec.image = rec.patient_id.image
            del records_ids, not_sync_img
        return

    # override copy function
    def copy(self, default=None):
        default = dict(default or {})
        default.update(name=_("%s (copy)") % self.name or '')
        return super(HospitalAppointment, self).copy(default)

    # override name search method
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            records = self.search(['|', ('contact', operator, name), ('name', operator, name)])
            return records.name_get()
        return self.search([('name', operator, name)]+args, limit=limit).name_get()

    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = record.doctor_id.display_name + ' | ' + record.doctor_id.specialization
    #         result.append((record.id, name))
    #     return result
