from odoo import api, exceptions, fields, models, _


class GymBatch(models.Model):
    _name = "gymwale.batch"
    _description = "GymWale Batch"
    _rec_name = "batch_name"

    batch_name = fields.Char('Batch Name')
    batch_starts = fields.Char('Batch Starts')
    batch_ends = fields.Char('Batch Ends')
    created_by = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user)

    def name_get(self):
        result = []
        for batch in self:
            name = ' | '.join((batch.batch_name, batch.batch_starts, batch.batch_ends))
            result.append((batch.id, name))
        return result
