# Copyright 2024 Angkot
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    'name': 'Angkot LOLO Depot Management',
    # Bump version to ensure updated security data is loaded without deprecated fields.
    'version': '1.0.2',
    'author': 'Angkot',
    'website': 'https://example.com',
    'category': 'Operations/Depot',
    'summary': 'Depot management for gate-in/out, invoicing, and yard control.',
    'depends': ['base', 'account', 'contacts', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/product_data.xml',
        'views/container_views.xml',
        'views/yard_location_views.xml',
        'views/gate_transaction_views.xml',
        'views/menu_items.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
