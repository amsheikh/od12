# -*- coding: utf-8 -*-
{
    'name': "add_payment_to_cash_register",

    'summary': """
        Add a line to cash statement after payment/Invoice payment
        """,

    'description': """

    """,

    'author': "Vitek",
    'website': "http://www.vi-tek.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/payment.xml',
        'views/journal.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
