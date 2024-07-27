
from odoo import api, exceptions, fields, models, _
from datetime import timedelta, date
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
today_date = date.today()
import random

day = ('monday', 'tuesday', 'wednesday', 'thrusday', 'friday', 'saturday')
workout = ['chest/biceps/forarms', 'shoulder-back/triceps', 'abs/legs/forarms',
           'chest/abs', 'shoulder-back/legs', 'biceps/triceps/forarms']


class GymMembers(models.Model):
    _name = "gymwale.members"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "GymWale Members"
    _rec_name = "name"
    _order = "name"

    serial_number = fields.Char('Serial Number')
    image = fields.Binary("Image", copy=False)
    name = fields.Char('Name', required=True)
    age = fields.Integer('Age')
    contact = fields.Char('Contact', required=True, copy=False)
    aadhaar_number = fields.Char('Aadhaar Number')
    address = fields.Text('Address')
    email = fields.Char('Email', copy=False)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    emergency_contact = fields.Char('Emergency Contact', copy=False)
    emergency_contact_name = fields.Char('Emergency Person Name and Relation')
    prior_health_issue = fields.Selection([('yes', 'Yes'), ('no', 'No'), ('long', 'Long Time Ago')],
                                          string='Any Prior Health Issue?')
    objective = fields.Selection([('cardio', 'Cardio'), ('strength', 'Strength'), ('cardio-strength', 'Cardio-Strength')],
                                string='Objective')
    membership_plan = fields.Many2one('gymwale.membership_plan', required=True)
    amount_to_be_paid = fields.Integer(string='Amount to be Paid')
    is_amount_paid = fields.Boolean(string='Is Amount Paid?', default=False)
    membership_assigned = fields.Date('Membership Assigned', required=True)
    membership_expire = fields.Date('Membership Expire')
    batch = fields.Many2one('gymwale.batch', 'Batch')
    discount = fields.Integer('Discount %', default=0)
    state = fields.Selection([('registered', 'Registered'), ('paid', 'Paid'), ('expire', 'Expired')],
                             string='Status', default='registered')
    day_counter = fields.Integer(compute='_compute_day_counter')
    last_cron_execute = fields.Date('Last Cron Execute')
    send_email = fields.Boolean('Send Email', default=True)
    measurement_ids = fields.One2many(comodel_name='member.measurement', inverse_name='member_id', string='Measurement')
    remark = fields.Char('Remark')
    active = fields.Boolean('Active', default=True)
    is_whatsapp_member = fields.Boolean('Is Whatsapp Member', default=False)
    is_member_joined = fields.Boolean('Is Member Joined', default=False)
    created_by = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user)

    _sql_constraints = [('contact_unique', 'unique (contact)', "Contact already exists !")]

    def get_monthly_collection(self, all_paid_members):
        arg = []
        membership_plan_ids = self.env['gymwale.membership_plan'].search([])
        monthly_id = membership_plan_ids.filtered(lambda x: x.membership.lower() == 'monthly')
        monthly_charges = monthly_id.mapped('membership_amount')[0]

        quarterly_id = membership_plan_ids.filtered(lambda x: x.membership.lower() == 'quarterly')
        quarterly_charges = quarterly_id.mapped('membership_amount')[0]

        half_yearly_id = membership_plan_ids.filtered(lambda x: x.membership.lower() == 'half yearly')
        half_yearly_charges = half_yearly_id.mapped('membership_amount')[0]

        monthly_members_total = sum(
            all_paid_members.filtered(lambda x: x.amount_to_be_paid <= monthly_charges).mapped('amount_to_be_paid'))
        quarterly_members_total = sum(
            all_paid_members.filtered(lambda x: monthly_charges < x.amount_to_be_paid <= quarterly_charges).mapped(
                'amount_to_be_paid'))
        half_yearly_members_total = sum(
            all_paid_members.filtered(lambda x: quarterly_charges < x.amount_to_be_paid <= half_yearly_charges).mapped(
                'amount_to_be_paid'))
        annual_members_total = sum(
            all_paid_members.filtered(lambda x: half_yearly_charges < x.amount_to_be_paid).mapped('amount_to_be_paid'))
        if monthly_members_total:
            arg.append(monthly_members_total)
        if quarterly_members_total:
            arg.append(quarterly_members_total // 3)
        if half_yearly_members_total:
            arg.append(half_yearly_members_total // 6)
        if annual_members_total:
            arg.append(annual_members_total // 12)
        monthly_collection = sum(arg) if arg else 0
        return monthly_collection

    @api.model
    def get_dashboard_info(self):
        # cache variable
        total_amount_collected = total_paid_members_count = 0
        total_paid_members = self.search([('is_amount_paid', '=', True)])
        total_paid_members_count = total_paid_members.__len__()
        all_paid_members = total_paid_members
        monthly_collection = self.get_monthly_collection(all_paid_members)
        collection = total_paid_members.mapped('amount_to_be_paid')
        total_collection = sum(collection)
        total_expense_records = self.env['gymwale.expense'].search([], order='bill_from desc', limit=1)
        total_gym_expense = total_expense_records.total_expense
        if monthly_collection and total_gym_expense:
            net_collection = monthly_collection - total_gym_expense
        return {
            'total_collection': total_collection,
            'total_paid_members_count': total_paid_members_count,
            'monthly_collection': monthly_collection,
            'total_gym_expense': total_gym_expense,
            'net_collection': net_collection,
        }


    def generate_routine(self):
        routine = {}
        count = 6
        while count != 0:
            random.shuffle(workout)
            today_workout = random.choice(workout)
            if today_workout not in routine.values():
                routine.update({day[6 - count]: today_workout})
                count -= 1
        form_view_id = self.env.ref('gymwale.gymwale_routine_generator_wizard').id
        return {
            'name': _('Routine Generator'),
            'view_type': 'form',
            'res_model': 'gymwale.routine_generator.wizard',
            'context': {'default_routine': routine},
            'view_id': form_view_id,
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window'
        }

    def membership_renew(self):
        self.write({
            'active': True,
            'state': 'registered',
            'discount': 0,
            'is_member_joined': True,
            'membership_expire': None,
            'amount_to_be_paid': 0,
            'membership_assigned': today_date
        })
        self.compute_expiry_date()
        self.compute_price()

    def unlink(self):
        """
        this function checks if the membership is paid it blocks the membership deletion
        :return:
        """
        for rec in self:
            if rec.is_amount_paid:
                raise ValidationError(_('Opps!! Paid Membership Record Can not be Deleted'))
        return super(GymMembers, self).unlink()

    @api.depends('membership_expire')
    def expired_membership_plan(self):
        """
        this function expires the membership once membership expire date has been passed
        and delete those unpaid client who do not get paid till 5 days from the registered date
        :return:
        """
        total_members = self.search([])
        expired_membership = total_members.filtered(lambda x: x.is_amount_paid and x.membership_expire < today_date)
        total_unpaid_members = total_members.filtered(lambda x: not x.is_amount_paid and not x.is_member_joined)
        for unpaid in total_unpaid_members:
            expiry_date = unpaid.membership_assigned if unpaid.state != 'expire' else unpaid.membership_expire
            expiry_date += timedelta(days=5)
            if expiry_date and expiry_date < today_date:
                if unpaid.state == 'registered':
                    unpaid.unlink()
                else:
                    unpaid.active = False
        for expired in expired_membership:
            expired.write({'state': 'expire', 'is_amount_paid': False, 'last_cron_execute': today_date,
                           'is_member_joined': False})

    @api.depends('membership_assigned', 'membership_expire')
    def _compute_day_counter(self):
        self.day_counter = 0
        if self.membership_expire and self.membership_assigned:
            difference = self.membership_expire - today_date
            self.day_counter = difference.days

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id, view_type, toolbar, submenu)
        remove_report_id = self.env.ref('gymwale.gymwale_membership_receipt').id
        if view_type == 'form' and remove_report_id and \
                toolbar and res['toolbar'] and res['toolbar'].get('print'):
            remove_report_record = [rec for rec in res['toolbar'].get('print') if rec.get('id') == remove_report_id]
            if remove_report_record and remove_report_record[0]:
                res['toolbar'].get('print').remove(remove_report_record[0])
        return res

    def print_membership_receipt_card(self):
        """
        this function send appointment email template when send email is true and
        download pdf appointment template
        :return:
        """
        membership_email_receipt_id = self.env.ref('gymwale.gymwale_email_receipt_template').id
        email_send_condition = (self.email, membership_email_receipt_id, self.send_email)
        if all(email_send_condition):
            mail_id = self.env['mail.template'].browse(membership_email_receipt_id).send_mail(self.id, force_send=True)
            if mail_id:
                msg = 'Invoice sent on email successfully'
            else:
                msg = 'Invoice sent on email failed'
            self.message_post(body=msg)
        self.send_email = False
        return self.env.ref('gymwale.gymwale_membership_receipt').report_action(self)

    def confirm_payment(self):
        self.write({'state': 'paid', 'is_amount_paid': True, 'is_member_joined': True})
        return

    @api.onchange('membership_plan', 'membership_assigned')
    def compute_expiry_date(self):
        self.membership_expire = False
        membership_period = self.membership_plan.membership_period
        if membership_period and self.membership_assigned:
            self.membership_expire = self.membership_assigned + timedelta(days=membership_period)

    @api.onchange('membership_plan', 'discount')
    def compute_price(self):
        self.amount_to_be_paid = 0
        amount = self.membership_plan.membership_amount
        if amount:
            self.amount_to_be_paid = amount * (100 - self.discount) * 0.01

    @api.model
    def create(self, vals):
        """
        this function generates the unique appointment ids for each new appointment created
        :param vals:
        :return:
        """
        if not vals.get('serial_number'):
            vals['serial_number'] = self.env['ir.sequence'].next_by_code('gymwale.members') or _('New')
        res = super(GymMembers, self).create(vals)
        return res
