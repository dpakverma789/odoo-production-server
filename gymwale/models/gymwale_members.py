
from odoo import api, exceptions, fields, models, _
from datetime import timedelta, date, datetime
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
today_date = date.today()
import random
import re
import json

day = ('monday', 'tuesday', 'wednesday', 'thrusday', 'friday', 'saturday')
workout = ['chest/biceps/forearms', 'shoulder-back/triceps', 'abs/legs',
           'chest/abs', 'shoulder-back/legs', 'biceps/triceps/forearms']
plan = {'Monthly': 1, 'Quarterly': 3, 'Half Yearly': 6, 'Annual': 12}


class GymMembers(models.Model):
    _name = "gymwale.members"
    _description = "GymWale Members"
    _rec_name = "name"
    _order = "membership_assigned desc"

    serial_number = fields.Char('Serial Number')
    # image = fields.Binary("Image", copy=False)
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
                                          string='Any Prior Health Issue?', default='no')
    objective = fields.Selection([('cardio', 'Cardio'), ('strength', 'Strength'), ('cardio-strength', 'Cardio-Strength')],
                                string='Objective', default='cardio-strength')
    membership_plan_id = fields.Many2one('gymwale.membership_plan', required=True)
    amount_to_be_paid = fields.Integer(string='Amount to be Paid')
    amount_from_referral = fields.Integer('Referral Amount')
    referral_amount = fields.Integer(string='Referral Discount', default=0)
    is_amount_paid = fields.Boolean(string='Is Amount Paid?', default=False)
    membership_assigned = fields.Date('Membership Assigned', required=True)
    membership_expire = fields.Date('Membership Expire')
    batch_id = fields.Many2one('gymwale.batch', 'Batch')
    discount = fields.Integer('Discount %', default=0)
    state = fields.Selection([('registered', 'Registered'), ('paid', 'Paid'), ('expire', 'Expired')],
                             string='Membership Status', default='registered')
    day_counter = fields.Char(compute='_compute_day_counter')
    # last_cron_execute = fields.Date('Last Cron Execute')
    send_email = fields.Boolean('Send Email', default=True)
    measurement_ids = fields.One2many(comodel_name='member.measurement', inverse_name='member_id', string='Measurement')
    remark = fields.Char('Remark')
    active = fields.Boolean('Active', default=True)
    is_whatsapp_member = fields.Boolean('Is Whatsapp Member', default=False)
    is_member_joined = fields.Boolean('Is Member Joined', default=False)
    follow_up = fields.Boolean('Client Follow Up', compute='_compute_follow_up')
    registration_charges = fields.Boolean('Registration Charges', default=True)
    block_reminder = fields.Boolean('Block Reminder', default=False)
    to_be_return = fields.Integer('Amount To Be Return', compute='_compute_amount_to_be_return')
    to_be_handover = fields.Integer('Amount To Be Handover')
    created_by = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user)
    transaction_date = fields.Datetime(string='Transaction date')

    _sql_constraints = [('contact_unique', 'unique (contact)', "Contact already exists !")]

    def get_monthly_collection(self, all_paid_members):
        arg = []
        membership_plan_ids = self.env['gymwale.membership_plan'].search([])
        monthly_id = membership_plan_ids.filtered(lambda x: x.membership.lower() == 'monthly')
        monthly_charges = monthly_id.mapped('membership_amount')[0] if monthly_id else 0

        quarterly_id = membership_plan_ids.filtered(lambda x: x.membership.lower() == 'quarterly')
        quarterly_charges = quarterly_id.mapped('membership_amount')[0] if quarterly_id else 0

        half_yearly_id = membership_plan_ids.filtered(lambda x: x.membership.lower() == 'half yearly')
        half_yearly_charges = half_yearly_id.mapped('membership_amount')[0] if half_yearly_id else 0

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

    @staticmethod
    def get_date_filters(date_filter, start_date=None, end_date=None):
        if date_filter == 'this_month':
            start_date = datetime.today().replace(day=1).date()
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        elif date_filter == 'last_month':
            first_day_of_current_month = datetime.today().replace(day=1)
            end_date = first_day_of_current_month - timedelta(days=1)
            start_date = end_date.replace(day=1)
        elif date_filter == '3_months':
            end_date = datetime.today().date()
            start_date = end_date - timedelta(days=90)
        elif date_filter == 'custom_range' and start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            # Default to some date range if needed
            start_date = datetime.today().replace(day=1).date()
            end_date = datetime.today().date()
        return start_date, end_date

    @api.model
    def get_dashboard_info(self, date_filter, start_date, end_date):
        # cache variable
        total_amount_collected = total_paid_members_count = net_collection = 0
        if date_filter:
            start_date, end_date = self.get_date_filters(date_filter, start_date, end_date)
        total_paid_members = self.search([('is_amount_paid', '=', True)])
        total_paid_members_count = total_paid_members.__len__()
        all_paid_members = total_paid_members
        monthly_collection = self.get_monthly_collection(all_paid_members)
        collection = total_paid_members.mapped('amount_to_be_paid')
        total_collection = sum(collection)
        total_expense_records = self.env['gymwale.expense'].search([], order='bill_from desc', limit=1)
        total_gym_expense = total_expense_records.total_expense
        net_collection = monthly_collection - total_gym_expense
        return {
            'total_collection': total_collection,
            'total_paid_members_count': total_paid_members_count,
            'monthly_collection': monthly_collection,
            'total_gym_expense': total_gym_expense,
            'net_collection': net_collection,
        }

    @api.onchange('amount_from_referral')
    def calculate_referral_amount(self):
        """
        this function calculate and set referral amount.
        :return: none
        """
        self._origin.referral_amount = 0
        self._origin.referral_amount = self.amount_from_referral * 10 * 0.01
        return

    def _compute_follow_up(self):
        """
        this function set follow-up flag based on some computation, for the customer to follow-up them.
        it sets True if client is not regular more than 10 days, so they can be followed up
        :return: none
        """
        self.follow_up = False
        inactive_records = self.search([('active', '=', False), ('state', '=', 'expire')])
        for rec in inactive_records:
            difference = today_date - rec.membership_expire
            days = difference.days
            rec.follow_up = True if abs(days) < 10 else False

    def _compute_amount_to_be_return(self):
        self.to_be_return = self.to_be_handover = False
        to_be_return = 0
        nearest_membership = {12: 6, 6: 3, 3: 1}
        membership_months = plan[self.membership_plan_id.membership]
        month, days, total_days = self._compute_day_counter()
        # ----------------- Refund -------------------
        month = month + 1 if month == 1 and days > 21 else month
        if membership_months >= 3:
            nearest_membership_month = nearest_membership[membership_months]
            if nearest_membership_month == 1:
                to_be_return = self.amount_to_be_paid - ((3 - month)*700)
            if nearest_membership_month == 3:
                to_be_return = self.amount_to_be_paid - ((6 - month)*600)
            if nearest_membership_month == 6:
                to_be_return = self.amount_to_be_paid - ((12 - month)*500)
        self.to_be_return = to_be_return if to_be_return > 1 else False

    def generate_routine(self):
        """
        this function generate exercise routine for the customer.
        :return: wizard
        """
        routine = {}
        count = 6
        while count != 0:
            random.shuffle(workout)
            today_workout = random.choice(workout)
            if today_workout not in routine.values():
                routine.update({day[6 - count]: today_workout})
                count -= 1
        routine = json.dumps(routine, indent=4)
        form_view_id = self.env.ref('gymwale.gymwale_routine_generator_wizard').id
        self.block_reminder = True
        return {
            'name': _('Routine Generator'),
            'view_type': 'form',
            'res_model': 'gymwale.routine_generator.wizard',
            'context': {
                'default_routine': routine,
                'default_member_id': self.id,
                'default_last_date': self.membership_expire + timedelta(days=5)
            },
            'view_id': form_view_id,
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window'
        }

    def membership_renew(self):
        """
        this function re-new the customer membership, so customer can re-register them-self again
        :return: none
        """
        self.write({
            'active': True,
            'state': 'registered',
            'discount': 0,
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
                    unpaid.write({
                        'active': False,
                        'registration_charges': True
                    })
        for expired in expired_membership:
            expired.write({'state': 'expire', 'is_amount_paid': False, 'is_member_joined': False,
                           'registration_charges': False, 'send_email': False})

    @api.depends('membership_assigned', 'membership_expire')
    def _compute_day_counter(self):
        self.day_counter = None
        if self.membership_expire and self.membership_assigned:
            difference = self.membership_expire - today_date
            days = difference.days
            self.day_counter = f'{days // 30} Months {days % 30} Days' if abs(days) > 30 else days
            return days // 30, days % 30, days

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
        email_send_condition = (self.email, membership_email_receipt_id, self.send_email, self.amount_to_be_paid)
        if all(email_send_condition):
            self.env['mail.template'].browse(membership_email_receipt_id).send_mail(self.id, force_send=True)
        self.send_email = False
        return self.env.ref('gymwale.gymwale_membership_receipt').report_action(self)

    def confirm_payment(self):
        self.write({'state': 'paid', 'referral_amount': 0, 'amount_from_referral': 0,
                   'is_amount_paid': True, 'is_member_joined': True, 'send_email': True, 'block_reminder': False,
                    'transaction_date': datetime.now()})
        self.print_membership_receipt_card()
        return

    @api.onchange('membership_plan_id', 'membership_assigned')
    def compute_expiry_date(self):
        self.membership_expire = False
        membership_period = self.membership_plan_id.membership_period
        if membership_period and self.membership_assigned:
            self.membership_expire = self.membership_assigned + timedelta(days=membership_period)

    @api.onchange('membership_plan_id', 'discount')
    def compute_price(self):
        self.amount_to_be_paid = 0
        self.batch_id = None
        amount = self.membership_plan_id.membership_amount
        if self.registration_charges:
            amount += 0
        if amount:
            pay_amount = amount * (100 - self.discount) * 0.01
            net_pay_amount = pay_amount - self.referral_amount
            self.amount_to_be_paid = net_pay_amount if net_pay_amount > 0 else 0

    @api.onchange('batch_id')
    def compute_common_batch_price(self):
        """
        this function compute the amount to be paid by customer if they opted the common batch for the gym.
        :return: none
        """
        if self.batch_id:
            if self.membership_plan_id.membership:
                number_of_months = plan[self.membership_plan_id.membership]
                if bool(re.search(r'\bcommon\b', self.batch_id.batch_name, re.IGNORECASE)):
                    self.amount_to_be_paid += (number_of_months * 300)
            else:
                raise ValidationError('Select Membership Plan First')

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