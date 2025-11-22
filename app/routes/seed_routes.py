from flask import Blueprint, jsonify
from seed_data import seed_data  # adjust this import to match your file

seed_bp = Blueprint("seed", __name__)


@seed_bp.route("/run-seed")
def run_seed():
    try:
        seed_data()  # Run your seeding logic
        return jsonify({"status": "success", "message": "Database seeded!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
