## -*- coding: utf-8 -*-

#from odoo import api, fields, models, _


#class AccountCommonReport(models.TransientModel):
#    _name = "account.common.report"
#    _description = "Account Common Report"

#    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
#    journal_ids = fields.Many2many('account.journal', string='Journals', required=True, default=lambda self: self.env['account.journal'].search([]))
#    date_from = fields.Date(string='Start Date')
#    date_to = fields.Date(string='End Date')
#    target_move = fields.Selection([('posted', 'All Posted Entries'),
#                                    ('all', 'All Entries'),
#                                    ], string='Target Moves', required=True, default='posted')

#    def _build_contexts(self, data):
#        result = {}
#        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
#        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
#        result['date_from'] = data['form']['date_from'] or False
#        result['date_to'] = data['form']['date_to'] or False
#        result['strict_range'] = True if result['date_from'] else False
#        return result

#    def _print_report(self, data):
#        raise NotImplementedError()

#    @api.multi
#    def check_report(self):
#        self.ensure_one()
#        data = {}
#        data['ids'] = self.env.context.get('active_ids', [])
#        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
#        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
#        used_context = self._build_contexts(data)
#        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
#        return self._print_report(data)
