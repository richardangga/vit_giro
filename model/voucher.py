from odoo import models, fields, api, _
import time
import logging
import odoo.addons.decimal_precision as dp
import datetime

# from openerp import tools
# from openerp.osv import fields,osv
# import openerp.addons.decimal_precision as dp
# import time
# import logging
# from openerp.tools.translate import _
# from openerp import netsvc

# _logger = logging.getLogger(__name__)

####################################################################################
# periodic read dari ca_pembayaran
# if exists create payment voucher for the invoice
####################################################################################
class account_voucher(models.Model):
    _name = "account.voucher"
    _inherit = "account.voucher"
    
    ####################################################################################
    # create payment
    # invoice_id: yang mau dibayar
    # journal_id: payment method
    ####################################################################################
    @api.model
    def create_payment(self, inv, partner_id, amount, journal, type, name, company_id):
        voucher_lines = []
        
        # cari move_line yang move_id nya = invoice.move_id
        move_line_id = self.env['account.move.line'].search([('move_id', '=', inv.move_id.id)])
        # move_lines = self.env['account.move.line'].browse(move_line_id)
        move_line = move_line_id[0]  # yang AR saja
        
        #payment supplier
        if type == 'payment':
            line_amount = amount
            line_type = 'dr'
            journal_account = journal.default_credit_account_id.id
        #receive customer
        else:
            line_amount = amount
            line_type = 'cr'
            journal_account = journal.default_debit_account_id.id
            
        
        voucher_lines.append((0, 0, {
            'move_line_id': move_line.id,
            'account_id': move_line.account_id.id,
            'amount_original': line_amount,
            'amount_unreconciled': line_amount,
            'reconcile': True,
            'amount': line_amount,
            'type': line_type,
            'name': move_line.name,
            'price_unit' : move_line.product_id.lst_price,
            'company_id': company_id
        }))
        
        voucher_id = self.env['account.voucher'].create({
            'partner_id' : partner_id,
            'amount' 		: amount,
            'account_id'	: journal_account,
            'journal_id'	: journal.id,
            'reference' 	: 'Payment giro ' + name,
            'name' 			: 'Payment giro ' + name,
            'company_id' 	: company_id,
            'type'			: type,
            'line_ids'		: voucher_lines
        })
        # _logger.info("   created payment id:%d" % (voucher_id) )
        return voucher_id
    
    ####################################################################################
    # set done
    ####################################################################################
    # @api.model
    # def payment_confirm(self, vid):
        # wf_service = netsvc.LocalService('workflow')
        # wf_service.trg_validate('account.voucher', vid, 'proforma_voucher')
        # _logger.info("   confirmed payment id:%d" % (vid) )
        # self.env["account.move"].browse(id).signal_workflow("payment_confirm")
        # return True
    
    
    ####################################################################################
    # find invoice by number
    ####################################################################################
    @api.model
    def find_invoice_by_number(self):
        invoice_obj = self.env['account.invoice']
        invoice_id = invoice_obj.search([('number' ,'=', number)])
        invoice = invoice_obj.browse(invoice_id)
        return invoice
    
    ####################################################################################
    # find journal by code
    ####################################################################################
    @api.model
    def find_journal_by_code(self):
        journal_obj = self.env['account.journal']
        journal_id = journal_obj.search([('code', '=', code)])
        journal = journal_obj.browse(journal_id)
        return journal