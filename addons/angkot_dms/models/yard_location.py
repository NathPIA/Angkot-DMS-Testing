from odoo import api, fields, models


class YardLocation(models.Model):
    _name = 'angkot.yard.location'
    _description = 'Depot Yard Location'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    parent_id = fields.Many2one('angkot.yard.location', string='Parent Location', index=True)
    child_ids = fields.One2many('angkot.yard.location', 'parent_id', string='Child Locations')
    location_type = fields.Selection([
        ('yard', 'Yard'),
        ('zone', 'Zone'),
        ('row', 'Row'),
        ('slot', 'Stack/Tier'),
    ], default='slot', required=True)
    capacity = fields.Integer(default=0)
    allowed_size = fields.Char(help='Optional size/type hint such as 20GP, 40HC')
    sequence = fields.Integer(default=10)
    gate_transaction_ids = fields.One2many('angkot.gate.transaction', 'yard_location_id', string='Assigned Transactions')
    current_container_count = fields.Integer(compute='_compute_current_container_count')

    @api.depends('gate_transaction_ids.state')
    def _compute_current_container_count(self):
        for location in self:
            location.current_container_count = len(
                location.gate_transaction_ids.filtered(
                    lambda gt: gt.state in ('in_progress', 'gated_in', 'invoiced')
                )
            )
