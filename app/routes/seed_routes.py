from flask import Blueprint, jsonify, current_app
from seed_data import seed_demo_data

seed_bp = Blueprint("seed", __name__)


@seed_bp.route("/run-seed")
def run_seed():
    try:
        seed_demo_data(current_app)  # Use *current* running app
        return jsonify({"status": "success", "message": "Database seeded!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
