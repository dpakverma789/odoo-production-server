{
    "name": "Money Management",
    'summary': "Money Management.",
    'description': """Money Management""",
    'author': "Deepak Verma",
    'website': "",
    'maintainer': 'Deepak Verma',
    'support': 'Deepak Verma',
    'version': '1.0.0',
    'depends': ['base', 'website', 'mail'],
    'data': [
        # security files
        'security/ir.model.access.csv',

        # wizard files
        'wizards/credit_bill_notification_wizard.xml',


        # reports files

        # views files
        'views/expense_category.xml',
        'views/expense_transaction.xml',
        'views/credit_card_manager.xml',
        'views/expense_bank_card.xml',

        # data files
        'data/cron.xml',

    ],
    'demo': [
        # demo data files
        'demo/demo_data.xml'

    ],
    'qweb': [],
    'sequence': '1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3'
}