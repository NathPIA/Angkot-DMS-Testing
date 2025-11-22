from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class Container(models.Model):
    _name = 'angkot.container'
    _description = 'Depot Container'
    _rec_name = 'container_number'
    _order = 'container_number'

    container_number = fields.Char(required=True, index=True)
    size_type = fields.Char(string='Size/Type')
    status = fields.Selection([
        ('empty', 'Empty'),
        ('laden', 'Laden'),
    ], default='empty', required=True)
    shipping_line_id = fields.Many2one('res.partner', string='Shipping Line')
    booking_no = fields.Char(string='Booking No')
    seal_no = fields.Char(string='Seal No')
    active = fields.Boolean(default=True)
    gate_transaction_ids = fields.One2many('angkot.gate.transaction', 'container_id', string='Gate Transactions')

    @api.constrains('container_number')
    def _check_container_number_format(self):
        pattern = re.compile(r'^[A-Z]{4}\d{7}$')
        for record in self:
            if record.container_number and not pattern.match(record.container_number.upper()):
                raise ValidationError(_('Container number must follow the format AAAA1234567.'))

    @api.constrains('container_number', 'active')
    def _check_unique_active_container(self):
        for record in self:
            if not record.container_number or not record.active:
                continue
            domain = [
                ('id', '!=', record.id),
                ('container_number', '=', record.container_number),
                ('active', '=', True),
            ]
            if self.search_count(domain):
                raise ValidationError(_('An active container with this number already exists.'))
