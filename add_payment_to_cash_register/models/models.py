# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
from datetime import date, datetime, timedelta
# class add_payment_to_cash_register(models.Model):
#     _name = 'add_payment_to_cash_register.add_payment_to_cash_register'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
class Payment(models.Model):
    _inherit = 'account.payment'
    cash_register_id = fields.Many2one('account.bank.statement',
        ondelete='set null',domain=lambda self:[('state', '=', 'open'),('journal_id','=',self.journal_id.id),('date', '=', str(datetime.now().date())),('company_id','child_of',[self.env.user.company_id.id])])

    registered = fields.Boolean(default=False)
    register = fields.Boolean(string="Add to cash register")
    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:

            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
            user = self.env.user
            for r in self:
                payment_journal = r.journal_id.id
                r.cash_register_id = self.env['account.bank.statement'].search([('state', '=', 'open'),('journal_id', '=', self.journal_id.id),('date', '=', str(datetime.now().date()))], limit=1)
            return {
            'domain': {
            'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)],
            'cash_register_id': [('state', '=', 'open'),('journal_id', '=', self.journal_id.id),('date', '=', str(datetime.now().date())),('company_id','child_of',[self.env.user.company_id.id])]}
            }
        return {}
    @api.multi
    def post(self):
        res = super(Payment, self).post()

        cash_statement_line=self.env['account.bank.statement.line']
        #company=self.env['res.company']._company_default_get('account.invoice')
        for column in self:
            cash_register_id=column.cash_register_id.id
            date=column.payment_date
            if column.register and not column.registered:
                for r in self:
                    inserted_cash_statement_line=cash_statement_line.create({
                    'name':r.name,
                    'amount':r.amount if r.payment_type == 'inbound' else r.amount * -1,
                    'date':date,
                    'ref':r.communication,
                    'statement_id':cash_register_id,
                    'partner_id':r.partner_id.id,
                    })
                self.write({
                    'registered': True,
                })

                return res




    @api.onchange('payment_date')
    def _onchange_payment_date(self):
        for r in self:
            payment_journal = r.journal_id.id
            r.cash_register_id = self.env['account.bank.statement'].search(
            [('state', '=', 'open'),
            ('journal_id', '=', self.journal_id.id),
            ('date', '=', str(self.payment_date))], limit=1)
        return {
        'domain': {
        'cash_register_id': [
        ('state', '=', 'open'),
        ('journal_id', '=', self.journal_id.id),
        ('date', '=', str(self.payment_date)),
        ('company_id','child_of',[self.env.user.company_id.id])
        ]}
        }
class AccountJournal(models.Model):
    _inherit = 'account.journal'
    auto_creation = fields.Boolean(default=False,string="Auto statement creation")
class CashRegisterScheduler(models.Model):
    _name = 'add_payment_to_cash_register.cash_register_scheduler'
    @api.model
    @api.multi
    def create_cash_register(self):
        journals_objs = self.env['account.journal'].search([('type', '=', 'cash')])
        for journals_obj in journals_objs:
            if journals_obj.auto_creation:
                cash_statement_obj = self.env['account.bank.statement']
                cash_statement_data = {
                    'name':str(journals_obj.name) + ' - ' + str(datetime.now().date()),
                    'journal_id':  journals_obj.id,
                    'date': datetime.now().date(),
                }
                cash_statement_obj.create(cash_statement_data)
