"""
Web Routes Module - Photo Organizer Dashboard

Rotas web para interface do usuário.
"""

from flask import render_template


def register_web_routes(app):
    """Registra todas as rotas web no app Flask."""

    @app.route("/")
    def index():
        """Página principal do dashboard."""
        return render_template("dashboard.html")