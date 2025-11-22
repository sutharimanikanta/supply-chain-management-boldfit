from flask import Blueprint, jsonify
from app import create_app
from seed_data import seed_demo_data

seed_bp = Blueprint("seed", __name__)


@seed_bp.route("/run-seed")
def run_seed():
    app = create_app()
    try:
        seed_demo_data(app)
        return jsonify({"status": "success", "message": "Database seeded!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
