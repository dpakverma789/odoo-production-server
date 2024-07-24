from odoo import models, fields, api


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = "res.config.settings"

    discard_days = fields.Integer('Discard Confirmed Appointment in Days')

    def get_values(self):
        res = super(ResConfigSettingsInherit, self).get_values()
        discard_days = self.env['ir.config_parameter'].sudo().get_param('discard_days')
        res.update({'discard_days': discard_days if discard_days else False})
        return res

    def set_values(self):
        super(ResConfigSettingsInherit, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('discard_days', self.discard_days or False)
