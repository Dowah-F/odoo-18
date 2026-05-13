{
    'name': 'Patient Management',
    'version': '19.0.1.0.0',
    'category': 'Healthcare',
    'summary': 'Manage hospital patients and their assigned doctors',
    'author': 'Huy Nguyen',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/patient_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
