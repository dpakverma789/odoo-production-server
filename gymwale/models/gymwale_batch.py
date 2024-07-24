from odoo import api, exceptions, fields, models, _


class GymBatch(models.Model):
    _name = "gymwale.batch"
    _description = "GymWale Batch"
    _rec_name = "batch_name"

    batch_name = fields.Char('Batch Name')
    batch_starts = fields.Char('Batch Starts')
    batch_ends = fields.Char('Batch Starts')
