# from openerp import tools
# from openerp.osv import fields, osv
# import openerp.addons.decimal_precision as dp
# import time
# import logging
# from openerp.tools.translate import _
# from openerp import netsvc
# from openerp import api

from odoo import models, fields, api, _
import time
import logging
import odoo.addons.decimal_precision as dp
import datetime

# _logger = logging.getLogger(__name__)
STATES = [('draft', 'Draft'), ('open', 'Open'), ('close', 'Close'), ('reject', 'Reject')]


class vit_giro(models.Model):
    _name = 'vit.giro'
    _description = 'Giro'
    
    def _get_invoices(self):
        results = {}
        for giro in self:
            results[giro.id] = ""
            for gi in giro.giro_invoice_ids:
                results[giro.id] += "%s " % (gi.invoice_id.number or "")
        return results

    name = fields.Char('Number', help='Nomor Giro', readonly=True, states={'draft': [('readonly', False)]})
    due_date = fields.Date('Due Date', help='', readonly=True, states={'draft': [('readonly', False)]})
    receive_date = fields.Datetime('Receive Date', help='', readonly=True, default=time.strftime("%Y-%m-%d %H:%M:%S"),
                                    states={'draft': [('readonly', False)]})
    clearing_date = fields.Datetime('Clearing Date', help='', readonly=True,
                                     states={'draft': [('readonly', False)]})
    amount = fields.Float('Amount', help='', readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', 'Partner', help='', readonly=True,
                                  states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', 'Bank Journal', domain=[('type', '=', 'bank')], help='',
                                  readonly=True, states={'draft': [('readonly', False)]})
    giro_invoice_ids = fields.One2many('vit.giro_invioce', 'giro_id', readonly=True,
                                        states={'draft': [('readonly', False)]})
    invoice_names = fields.Char(string="Allocated Invoices", compute='_get_invoices')
    type = fields.Selection([
        ('payment', 'Payment'),
        ('receipt', 'Receipt')],
        "Type",
        required=True, readonly=True, default='payment', states={'draft': [('readonly', False)]})
    invoice_type = fields.Char('Invoice Type', readonly=True, default='in_invoice', states={'draft': [('readonly', False)]})
    state = fields.Selection(string="State", selection=STATES, required=True, readonly=True, default=STATES[0][0])
    
    _sql_constraints = [('name_uniq', 'unique(name)', _('Nomor Giro tidak boleh sama'))]
    
    def _cek_total(self):
        inv_total = 0.0
        for giro in self:
            for gi in giro.giro_invoice_ids:
                inv_total += gi.amount
            
            if giro.amount == inv_total:
                return True
        
        return False
    
    _constraints = [(_cek_total, _('Total amount allocated for the invoices must be the same as total Giro amount'),
                     ['amount', 'giro_invoice_ids'])]

    @api.multi
    def action_cancel(self):
        data = {'state': STATES[0][0]}
        self.write(data)
    
    @api.multi
    def action_confirm(self):
        data = {'state': STATES[1][0]}
        self.write(data)
    
    @api.multi
    def action_clearing(self):
        
        # voucher_obj = self.env['account.voucher']
        # users_obj = self.env['res.users']
        # u1 = users_obj
        # company_id = u1.company_id.id
        
        # for giro in self:
        #     for gi in giro.giro_invoice_ids:
        #         invoice_id = gi.invoice_id
        #         partner_id = giro.partner_id.id
        #         amount = gi.amount
        #         journal_id = giro.journal_id
        #         type = giro.type
        #         name = giro.name
        #         vid = voucher_obj.create_payment(invoice_id, partner_id, amount, journal_id, type, name,
        #                                          company_id)
                # voucher_obj.payment_confirm(vid)

        
        # av = self.env['account.voucher']
        # company_id = self._context.get('company_id', self.env.user.company_id.id)
        # journal = self.env['account.journal']

        # for giro in self:
        #     voucher_lines = []
        #     av = giro.env['account.voucher']
        #     company_id = giro._context.get('company_id', giro.env.user.company_id.id)
        #     journal = giro.env['account.journal']            
        #     #payment supplier
        #     if giro.type == 'payment':
        #         line_type = 'purchase'
        #         journal_account = giro.journal_id.default_credit_account_id.id
        #         journal_type = journal.search([("type", "=", "purchase")], limit=1)
        #     #receive customer
        #     else:
        #         line_type = 'sale'
        #         journal_account = giro.journal_id.default_debit_account_id.id
        #         journal_type = journal.search([("type", "=", "sale")], limit=1)
        #     for gi in giro.giro_invoice_ids:
        #         for gi_line in gi.invoice_id.invoice_line_ids:
        #             voucher_lines.append( (0,0,{
        #                 'product_id'    : gi_line.product_id.id,
        #                 'name'    : gi_line.name,
        #                 'account_id'    : gi_line.account_id.id,
        #                 'quantity'    : gi_line.quantity,
        #                 'price_unit': gi_line.price_unit,
        #                 'price_subtotal'    : gi_line.price_subtotal,
        #             }) )
            
        #     voucher_id = av.create({
        #         'voucher_type'      : line_type,
        #         'partner_id'        : giro.partner_id.id,
        #         'pay_now'           : 'pay_now',
        #         'account_id'        : journal_account,
        #         'payment_journal_id': giro.journal_id.id,
        #         'journal_id'        : journal_type.id,
        #         'reference'         : 'Payment giro ' + self.name,
        #         'name'              : 'Payment giro ' + self.name,
        #         'company_id'        : company_id,
        #         'line_ids'          : voucher_lines,

        #     })
        #     # import pdb; pdb.set_trace()
        #     av.browse(voucher_id.id).proforma_voucher() 
        
        #     data = {'state': STATES[2][0],
        #             'clearing_date': time.strftime("%Y-%m-%d %H:%M:%S")}
        #     self.write(data)

        for giro in self:
            payment = giro.env['account.payment']
            company_id = giro._context.get('company_id', giro.env.user.company_id.id)            
            #payment supplier
            if giro.type == 'payment':
                pay_type = 'outbound'
                partner_type = 'supplier'
                payment_method = giro.journal_id.outbound_payment_method_ids.id
            #receive customer
            else:
                pay_type = 'inbound'
                partner_type = 'customer'
                payment_method = giro.journal_id.inbound_payment_method_ids.id
                
            payment_id = payment.create({
                'payment_type'      : pay_type,
                'partner_id'        : giro.partner_id.id,
                'partner_type'      : partner_type,
                'journal_id'        : giro.journal_id.id,
                'amount'            : giro.amount,
                'communication'     : 'Payment giro ' + self.name,
                'company_id'        : company_id,
                'payment_method_id' : payment_method,

            })
            # import pdb; pdb.set_trace()
            payment.browse(payment_id.id).post() 
        
            data = {'state': STATES[2][0],
                    'clearing_date': time.strftime("%Y-%m-%d %H:%M:%S")}
            self.write(data)

        # return payment_id
    
    def action_reject(self):
        data = {'state': STATES[3][0]}
        self.write(data)
    
    @api.onchange('type')
    def on_change_type(self):
        inv_type = 'in_invoice'
        if self.type == 'payment':
            inv_type = 'in_invoice'
        elif self.type == 'receipt':
            inv_type = 'out_invoice'
        self.invoice_type = inv_type


class vit_giro_invoice(models.Model):
    _name = 'vit.giro_invioce'
    _description = 'Giro vs Invoice'
    
    
    giro_id = fields.Many2one('vit.giro', 'Giro', help='')
    invoice_id = fields.Many2one('account.invoice', 'Invoice',
                                  help='Invoice to be paid',
                                  domain=[('state', '=', 'open')])
    # 'amount_invoice': fields.related("invoice_id", "residual",
    #             relation="account.invoice",
    #             type="float", string="Invoice Amount", store=True),
    amount_invoice = fields.Float('Invoice Amount')
    amount = fields.Float('Amount Allocated')
   
    
    @api.onchange('invoice_id')
    def on_change_invoice_id(self):
        self.amount_invoice = self.invoice_id.residual


class account_invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    
    giro_invoice_ids = fields.One2many('vit.giro_invioce', 'invoice_id', string="Giro")
    
