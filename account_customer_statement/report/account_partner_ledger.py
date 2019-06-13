# -*- coding: utf-8 -*-

import time
from openerp import api, models

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ReportPartnerLedger_statement(models.AbstractModel):
    _name = 'report.account_customer_statement.report_partnerledger_custom'

    def _lines(self, data, partner):
        full_account = []
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, inv.origin as origin, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
			LEFT JOIN account_invoice inv ON (inv.id = "account_move_line".invoice_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                ORDER BY "account_move_line".date, "account_move_line".id"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0
        for r in res:
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('origin' , 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            if r['currency_id'] is None:
                r['currency_id'] = self.env.user.company_id.currency_id.id
                r['currency_code'] = self.env.user.company_id.currency_id.symbol
                r['amount_currency'] = r['progress']
            full_account.append(r)
        return full_account

    def _sum_open_balance(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        result = 0.0
        context = {}
        context['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        context['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        context['date_from'] = False
        context['date_to'] = datetime.strptime(data['form']['date_from'], "%Y-%m-%d") + relativedelta(days = -1) or False
        context['strict_range'] = False
        query_get_data = self.env['account.move.line'].with_context(context)._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '



        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contempp = self.env.cr.fetchone()
        if contempp is not None:
            resultt = contempp[0] or 0.0
        return resultt
		
    def _sum_partner(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '

        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

#     @api.multi
#     def render_html(self, doc_ids, data):
    @api.model
    def _get_report_values(self, docids, data=None):
        data['computed'] = {}

        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.internal_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '
        print (":::::::::::::::::::::::::params",params)
        query = """
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND "account_move_line".account_id = account.id
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND NOT account.deprecated
                AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))
        #partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]#probuse
        partner_ids = data['form'].get('custom_partner_ids', [])#[self.env.context.get('active_id')]#probuse
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref, x.name))
        docargs = {
            'doc_ids': partner_ids,
            'doc_model': self.env['res.partner'],
            'data': data,
            'docs': partners,
            'time': time,
            'lines': self._lines,
            'sum_partner': self._sum_partner,
			'sum_open_balance': self._sum_open_balance,
        }
        print ("::::::::::::::::::::::::::::::::::;docargs",docargs)
        return docargs#odoo11
#         return self.env['report'].render('account_customer_statement.report_partnerledger', docargs)#odoo11
