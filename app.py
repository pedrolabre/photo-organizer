"""
Flask Web Application - Photo Organizer Dashboard

Servidor web local que fornece interface gráfica para organizar fotos.
"""

from flask import Flask
from src.utils.logger import init_logger
from src.routes.web_routes import register_web_routes
from src.routes.api_routes import register_api_routes

app = Flask(__name__)

# Estado global da aplicação
app_state = {
    "processing": False,
    "progress": {
        "stage": "",
        "current": 0,
        "total": 0,
        "percentage": 0,
        "message": "",
    },
    "last_result": None,
}

# Configura o estado global no app
app.config['APP_STATE'] = app_state

# Registra todas as rotas
register_web_routes(app)
register_api_routes(app)

if __name__ == "__main__":
    init_logger(level="INFO")
    print("=" * 60)
    print("🚀 Photo Organizer Dashboard")
    print("=" * 60)
    print()
    print("📡 Servidor iniciando...")
    print("🌐 Acesse: http://localhost:5000")
    print()
    print("⚠️  Pressione Ctrl+C para parar o servidor")
    print("=" * 60)
    print()
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
