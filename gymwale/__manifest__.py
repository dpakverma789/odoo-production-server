{
    'name': 'GymWale',
    'version': '1.0',
    'summary': 'GymWale',
    'sequence': 1,
    'description': """This module is for GymWale""",
    'category': 'Extra Tools',
    'website': 'https://gymwale.vercel.app/',
    'images': [],
    'depends': ['base','mail', 'web'],
    'data': [
        # security
        'security/ir.model.access.csv',

        # wizard
        'wizards/routine_generator.xml',

        # views
        'views/gymwale_members.xml',
        'views/gymwale_membership_plan.xml',
        'views/gymwale_batch.xml',
        'views/dashboard.xml',
        'views/gymwale_expense.xml',
        'views/member_measurement.xml',
        'views/menus.xml',

        # data
        'data/members_serial_code.xml',
        'data/ir_crons.xml',

        # demo data files
        'demo/demo_data.xml',

        #report
        'reports/gymwale_membership_receipt.xml',
        'reports/gymwale_membership_email_receipt.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'GymWale_CRM/static/src/js/gymwale_dashboard.js',
            'GymWale_CRM/static/src/css/dashboard.css',
            'GymWale_CRM/static/src/xml/gymwale_dashboard.xml'
        ],
    },


    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
