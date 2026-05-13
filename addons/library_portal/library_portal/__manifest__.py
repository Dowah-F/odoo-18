{
    'name': 'Library Portal',
    'version': '1.0',
    'summary': 'Quản lý mượn sách thư viện qua Portal và API',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    'application': True,
}