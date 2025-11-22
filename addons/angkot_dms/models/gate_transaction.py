from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class GateTransaction(models.Model):
    _name = 'angkot.gate.transaction'
    _description = 'Gate Transaction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    container_id = fields.Many2one('angkot.container', required=True, tracking=True)
    truck_plate = fields.Char(required=True)
    driver_name = fields.Char()
    driver_phone = fields.Char()
    service_type = fields.Selection([
        ('drop_off', 'Drop-off'),
        ('lift_off', 'Lift-off'),
        ('keep_empty', 'Keep Empty'),
        ('keep_laden', 'Keep Laden'),
        ('move_empty', 'Move Empty'),
        ('move_laden', 'Move Laden'),
        ('mt_return', 'MT Return'),
        ('transfer_mt', 'Transfer MT'),
        ('transfer_laden', 'Transfer Laden'),
    ], required=True, default='drop_off')
    state = fields.Selection([
        ('in_progress', 'In Progress'),
        ('gated_in', 'Gated In'),
        ('invoiced', 'Invoiced'),
        ('gate_out', 'Gate Out'),
        ('cancelled', 'Cancelled'),
    ], default='in_progress', tracking=True)
    gate_in_datetime = fields.Datetime(default=lambda self: fields.Datetime.now())
    gate_out_datetime = fields.Datetime()
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    shipping_line_id = fields.Many2one('res.partner', string='Shipping Line')
    booking_no = fields.Char()
    seal_no = fields.Char()
    yard_location_id = fields.Many2one('angkot.yard.location', string='Yard Location', tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)
    service_fee = fields.Monetary(default=0.0)
    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)

    @api.constrains('container_id', 'state')
    def _check_open_transaction_per_container(self):
        for record in self:
            domain = [
                ('id', '!=', record.id),
                ('container_id', '=', record.container_id.id),
                ('state', 'in', ['in_progress', 'gated_in', 'invoiced']),
            ]
            if self.search_count(domain):
                raise ValidationError(_('Another active gate transaction exists for this container.'))

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('angkot.gate.transaction') or 'New'
        return super().create(vals)

    def action_confirm_gate_in(self):
        for record in self:
            if record.state not in ('in_progress',):
                continue
            record.state = 'gated_in'
        return True

    def action_create_invoice(self):
        for record in self:
            if record.invoice_id:
                raise UserError(_('Invoice already exists for this gate transaction.'))
            if not record.partner_id:
                raise UserError(_('Please set a customer before invoicing.'))
            product = self.env.ref('angkot_dms.product_gate_service')
            price_unit = record.service_fee or product.list_price
            move_vals = {
                'move_type': 'out_invoice',
                'partner_id': record.partner_id.id,
                'invoice_origin': record.name,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': product.id,
                        'name': _('Gate handling for %s') % (record.container_id.container_number,),
                        'quantity': 1.0,
                        'price_unit': price_unit,
                    })
                ],
            }
            invoice = self.env['account.move'].create(move_vals)
            record.invoice_id = invoice.id
            record.state = 'invoiced'
        return True

    def action_gate_out(self):
        for record in self:
            if record.state not in ('gated_in', 'invoiced'):
                raise UserError(_('Only gated-in or invoiced transactions can be gated out.'))
            if record.invoice_id and record.invoice_id.state != 'posted':
                raise UserError(_('Invoice must be posted before gate-out.'))
            if record.invoice_id and record.invoice_id.payment_state not in ('paid', 'in_payment', 'partial'):
                raise UserError(_('Invoice must be paid or in payment before gate-out.'))
            record.gate_out_datetime = fields.Datetime.now()
            record.state = 'gate_out'
        return True

    def action_reset_to_draft(self):
        for record in self:
            if record.state == 'gate_out':
                raise UserError(_('Cannot reset a completed gate transaction.'))
            record.state = 'in_progress'
            record.gate_out_datetime = False
        return True
