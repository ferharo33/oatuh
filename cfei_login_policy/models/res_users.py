# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied


_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = "res.users"

    login_method = fields.Selection(
        selection=[("password", "Contraseña Odoo"), ("oauth", "Microsoft OAuth")],
        string="Método de acceso",
        default="password",
        help="Método de autenticación permitido para este usuario. Es exclusivo.",
    )

    # --- BLOQUEO: Login por contraseña cuando el usuario es OAuth-only ---
    def _check_credentials(self, password, env):
        self.ensure_one()
        policy = self.env["ir.config_parameter"].sudo().get_param(
            "cfei.auth_exclusive", "per_user"
        )
        # Si es política global oauth_only o a nivel usuario marcado como oauth, denegar
        if policy == "oauth_only" or (policy == "per_user" and self.login_method == "oauth"):
            _logger.info(
                "Login con contraseña bloqueado para usuario %s por política de exclusividad",
                self.login,
            )
            raise AccessDenied(_("Debes iniciar sesión con tu cuenta de Microsoft."))
        return super()._check_credentials(password, env)
    
    # --- BLOQUEO: Login por OAuth cuando el usuario es Password-only ---
    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        # Política global: solo password
        policy = self.env["ir.config_parameter"].sudo().get_param(
            "cfei.auth_exclusive", "per_user"
        )
        if policy == "password_only":
            _logger.info("OAuth bloqueado por política global password_only")
            raise Exception("Access Denied")

        email = str(validation.get("email") or "").strip().lower()
        user = self.search([("login", "=", email)], limit=1)
        if user and policy == "per_user" and user.login_method == "password":
            _logger.info(
                "OAuth bloqueado para usuario %s por política de exclusividad",
                user.login,
            )
            raise Exception("Access Denied")

        # Si se va a crear el usuario por autosignup, marcarlo como oauth
        # (el create real lo hace la super() del módulo Cybrosys si aplica)
        self = self.with_context(cfei_login_policy_mark_oauth=True)
        login = super()._auth_oauth_signin(provider, validation, params)
        # Asegura que el usuario asociado queda marcado como oauth
        if login:
            u = self.search([("login", "=", login)], limit=1)
            if u and u.login_method != "oauth":
                u.sudo().write({"login_method": "oauth"})
        return login
    
    # Hook en create para casos de autosignup fuera del flujo anterior
    @api.model
    def create(self, vals):
        if self.env.context.get("cfei_login_policy_mark_oauth") and not vals.get("login_method"):
            vals["login_method"] = "oauth"
        return super().create(vals)