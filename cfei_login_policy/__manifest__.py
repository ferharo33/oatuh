{
    "name": "CFEi Login Policy",
    "summary": "Política de acceso exclusivo por usuario (Password u OAuth)",
    "version": "17.0.1.0.0",
    "category": "Authentication",
    "author": "Teamfactory",
    "website": "https://teamfactory.cloud",
    "license": "LGPL-3",
    "depends": [
        "base",
        "auth_oauth",
        "auth_signup",
        "microsoft_azure_sso_integration", # asegura carga posterior al módulo de Cybrosys
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "views/res_users_views.xml",
    ],
    "installable": True,
}