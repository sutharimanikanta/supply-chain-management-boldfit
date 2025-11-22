from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from app.routes.warehouse_routes import warehouse_bp
    from app.routes.sku_routes import sku_bp
    from app.routes.inventory_routes import inventory_bp
    from app.routes.forecast_routes import forecast_bp
    from app.routes.transfer_routes import transfer_bp
    from app.routes.assistant_routes import assistant_bp
    from app.routes.dashboard_routes import dashboard_bp

    app.register_blueprint(warehouse_bp, url_prefix="/warehouses")
    app.register_blueprint(sku_bp, url_prefix="/skus")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(forecast_bp, url_prefix="/forecast")
    app.register_blueprint(transfer_bp, url_prefix="/transfers")
    app.register_blueprint(assistant_bp, url_prefix="/assistant")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    @app.route("/")
    def index():
        return render_template("index.html")

    # Create tables
    with app.app_context():
        db.create_all()

    return app
