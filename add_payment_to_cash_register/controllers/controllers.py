# -*- coding: utf-8 -*-
from odoo import http

# class AddPaymentToCashRegister(http.Controller):
#     @http.route('/add_payment_to_cash_register/add_payment_to_cash_register/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_payment_to_cash_register/add_payment_to_cash_register/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_payment_to_cash_register.listing', {
#             'root': '/add_payment_to_cash_register/add_payment_to_cash_register',
#             'objects': http.request.env['add_payment_to_cash_register.add_payment_to_cash_register'].search([]),
#         })

#     @http.route('/add_payment_to_cash_register/add_payment_to_cash_register/objects/<model("add_payment_to_cash_register.add_payment_to_cash_register"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_payment_to_cash_register.object', {
#             'object': obj
#         })